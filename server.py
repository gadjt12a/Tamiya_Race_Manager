#!/usr/bin/env python3
"""
Tamiya Race Manager - Local Server
Serves the app, handles data file read/write, and shuts down when the browser tab closes.
"""
import http.server
import json
import os
import shutil
import socketserver
import sys
import threading
import time
import webbrowser
from pathlib import Path

PORT = 8765

# When frozen into a single exe (PyInstaller), bundled resources (the HTML,
# VERSION file) unpack to a temp dir; legacy data is looked for next to the
# exe itself. In dev, both are simply this script's folder.
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
else:
    RESOURCE_DIR = APP_DIR = Path(__file__).parent
BASE_DIR = APP_DIR  # legacy alias

try:
    APP_VERSION = (RESOURCE_DIR / "VERSION").read_text().strip()
except Exception:
    APP_VERSION = "?"


def resolve_data_dir():
    """Race data lives OUTSIDE the app folder so installing/updating the app
    can never touch it. Override with TAMIYA_DATA_DIR for portable use."""
    override = os.environ.get("TAMIYA_DATA_DIR")
    if override:
        return Path(override)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "TamiyaRaceManager"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "TamiyaRaceManager"
    return Path.home() / ".tamiya-race-manager"


DATA_DIR = resolve_data_dir()
DATA_FILE = DATA_DIR / "racedata.json"
BACKUP_DIR = DATA_DIR / "backups"
BACKUP_KEEP = 14  # daily backups retained

# Where pre-v10 zip installs kept their data (next to the app)
LEGACY_DATA_FILE = BASE_DIR / "data" / "racedata.json"
LEGACY_BACKUP_DIR = BASE_DIR / "data" / "backups"
migrated_this_run = False


def migrate_legacy_data():
    """One-time move of race data to the new per-user location.
    COPIES, never moves - the old file is deliberately left in place as a
    fossil backup. Runs only when the new location has no data yet."""
    global migrated_this_run
    if DATA_FILE.exists() or not LEGACY_DATA_FILE.exists():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY_DATA_FILE, DATA_FILE)
    if LEGACY_BACKUP_DIR.is_dir():
        shutil.copytree(LEGACY_BACKUP_DIR, BACKUP_DIR, dirs_exist_ok=True)
    migrated_this_run = True
    print(f"  Race data copied to its new home: {DATA_FILE}")
    print(f"  (The old copy in {LEGACY_DATA_FILE.parent} was left untouched as a backup.)")
    try:
        (LEGACY_DATA_FILE.parent / "DATA-HAS-MOVED.txt").write_text(
            "Your race data now lives at:\n"
            f"  {DATA_FILE}\n\n"
            f"It was copied there on {time.strftime('%Y-%m-%d')} and this old copy was left\n"
            "in place as a backup. App updates can no longer touch your data.\n"
            "Do not use racedata.json in THIS folder - it is no longer updated.\n",
            encoding="utf-8",
        )
    except Exception:
        pass  # the note is a courtesy; never block startup over it


def backup_data_file():
    """Once per day, snapshot the data file as it was BEFORE today's first save
    (i.e. it preserves the previous race night's final state)."""
    try:
        if not DATA_FILE.exists():
            return
        dest = BACKUP_DIR / f"racedata-{time.strftime('%Y-%m-%d')}.json"
        if dest.exists():
            return
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DATA_FILE, dest)
        for old in sorted(BACKUP_DIR.glob("racedata-*.json"))[:-BACKUP_KEEP]:
            old.unlink()
    except Exception as e:
        # A backup problem must never block saving the live data
        print(f"  Warning: daily backup failed: {e}")

# ── Heartbeat watchdog ─────────────────────────────────────────────────────────
# The browser page sends a /ping every 5 seconds while open.
# If we don't receive a ping for 12 seconds, the tab has been closed → shut down.
HEARTBEAT_TIMEOUT = 12
NO_BROWSER_TIMEOUT = 300  # if no browser EVER connects, give up after 5 min
last_ping = time.time()
first_ping_seen = False   # countdown only starts once the browser has connected
server_ref = None

def watchdog():
    """Background thread - shuts down server if browser tab closes.
    - The close-detection countdown does not start until the browser has pinged
      at least once: a first run can be slowed by SmartScreen, antivirus scans
      or a cold browser start, and the server must wait for it.
    - Sleep-tolerant: if the wall clock jumps (laptop lid closed / machine
      slept), the browser never had a chance to ping, so reset the timer
      instead of killing the server out from under an open tab."""
    global last_ping
    start = time.time()
    last_check = time.time()
    while True:
        time.sleep(3)
        now = time.time()
        if now - last_check > 30:  # slept far past our 3s interval
            last_ping = now  # give the browser a fresh window to resume pinging
        last_check = now
        if not first_ping_seen:
            if now - start > NO_BROWSER_TIMEOUT:
                print("\n  No browser connected within 5 minutes - shutting down.")
                os._exit(0)
            continue
        if now - last_ping > HEARTBEAT_TIMEOUT:
            print("\n  Browser tab closed - shutting down. Goodbye!")
            if server_ref:
                threading.Thread(target=server_ref.shutdown, daemon=True).start()
            os._exit(0)


class RaceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RESOURCE_DIR), **kwargs)

    def _send_json(self, obj, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("utf-8"))

    def do_GET(self):
        global last_ping, migrated_this_run, first_ping_seen
        path_only = self.path.split("?")[0]

        if path_only == "/ping":
            last_ping = time.time()
            first_ping_seen = True
            self._send_json({"ok": True})
            return

        if path_only == "/info":
            # migrated flag is reported once so the app shows a one-time notice
            self._send_json({"dataDir": str(DATA_DIR), "migrated": migrated_this_run, "version": APP_VERSION})
            migrated_this_run = False
            return

        # The data file no longer lives under the app folder - serve it from
        # its real home so the app's existing fetch path keeps working.
        if path_only == "/data/racedata.json":
            try:
                self._send_json(json.loads(DATA_FILE.read_text(encoding="utf-8")))
            except FileNotFoundError:
                self._send_json({"error": "no data file"}, 404)
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        super().do_GET()

    def do_POST(self):
        global last_ping
        last_ping = time.time()

        if self.path == "/backup":
            # Tagged snapshot (e.g. pre-upgrade-v2) taken before a data migration
            length = int(self.headers.get("Content-Length", 0))
            try:
                tag = json.loads(self.rfile.read(length)).get("tag", "manual")
                tag = "".join(c for c in str(tag) if c.isalnum() or c in "-_")[:40] or "manual"
                if DATA_FILE.exists():
                    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(DATA_FILE, BACKUP_DIR / f"{tag}-{time.strftime('%Y-%m-%d-%H%M%S')}.json")
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            return

        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
                backup_data_file()
                tmp_file = DATA_FILE.with_suffix('.tmp')
                with open(tmp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(tmp_file, DATA_FILE)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'{{"error":"{str(e)}"}}'.encode())

        elif self.path == "/shutdown":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            print("\n  Shutdown requested - stopping server. Goodbye!")
            threading.Thread(target=lambda: (time.sleep(0.5), os._exit(0)), daemon=True).start()

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # suppress request logs

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()


def already_running():
    """True if another Race Manager instance is already serving on our port."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}/ping", timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


if __name__ == "__main__":
    APP_URL = f"http://localhost:{PORT}/race-manager.html"

    if already_running():
        print("  Race Manager is already running - opening it in your browser.")
        try:
            webbrowser.open(APP_URL)
        except Exception:
            print(f"  Could not open a browser - go to {APP_URL} manually.")
        time.sleep(2)
        sys.exit(0)

    migrate_legacy_data()  # copy (never move) pre-v10 data to the new home
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump({"version": 1, "seasons": [], "racers": [], "currentSeason": None}, f, indent=2)

    print("=" * 50)
    print(f"  TAMIYA RACE MANAGER v{APP_VERSION}")
    print("=" * 50)
    print(f"  Starting on http://localhost:{PORT}")
    print(f"  Data file: {DATA_FILE}")
    print()
    print("  Opens automatically in your browser.")
    print("  Closes automatically when you close the tab.")
    print("  Press Ctrl+C to stop manually.")
    print("=" * 50)

    socketserver.TCPServer.allow_reuse_address = True
    try:
        # 127.0.0.1 (not all interfaces): keeps the app private to this machine
        # and avoids the Windows Firewall "Allow access" prompt on first run.
        httpd = socketserver.TCPServer(("127.0.0.1", PORT), RaceHandler)
    except OSError:
        print()
        print(f"  ERROR: port {PORT} is in use by another program.")
        print("  Close the other program and try again, or restart the computer.")
        input("  Press Enter to close this window...")
        sys.exit(1)

    with httpd:
        server_ref = httpd
        t = threading.Thread(target=watchdog, daemon=True)
        t.start()
        # Server is bound and listening - NOW it is safe to open the browser
        try:
            webbrowser.open(APP_URL)
        except Exception:
            print(f"  Could not open a browser - go to {APP_URL} manually.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped. Goodbye!")
