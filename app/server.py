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

# Build number = commit count on the branch that produced this package
# (git rev-list --count HEAD), written by the build scripts. It ticks up
# with every pushed commit, so two packages built from the same commit are
# identical and two different commits can never be confused. "0" means the
# package was built without git available (e.g. from a source zip).
try:
    APP_BUILD = (RESOURCE_DIR / "BUILD").read_text().strip() or "0"
except Exception:
    APP_BUILD = "0"

if APP_BUILD == "0" and not getattr(sys, "frozen", False):
    # Running from a source checkout: app/BUILD is written by the build
    # scripts and is gitignored, so it isn't there. Ask git directly rather
    # than showing a misleading "<version>.0" in the header.
    try:
        import subprocess
        APP_BUILD = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(RESOURCE_DIR), capture_output=True, text=True, timeout=3
        ).stdout.strip() or "0"
    except Exception:
        APP_BUILD = "0"

# What the app header, console and installer all show, e.g. "9.39.412"
FULL_VERSION = f"{APP_VERSION}.{APP_BUILD}"


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
# If no ping arrives for HEARTBEAT_TIMEOUT seconds, the tab has been closed and
# the server shuts down.
#
# 12 seconds was FAR too tight and killed the app during a race night while it
# sat untouched. Browsers and WebViews throttle background timers hard - a
# window that is not focused can have its setInterval slowed to roughly once a
# minute - so an idle-but-open app stopped pinging often enough and the
# watchdog shot it. The only cost of a generous timeout is the server
# lingering a little longer after the tab really is closed, which nobody
# notices; the cost of it being too short is losing the app mid-event.
HEARTBEAT_TIMEOUT = 180
NO_BROWSER_TIMEOUT = 300  # if no browser EVER connects, give up after 5 min
last_ping = time.time()
first_ping_seen = False   # countdown only starts once the browser has connected
server_ref = None

# ── Second-screen display feed ─────────────────────────────────────────────────
# The coordinator app POSTs its display HTML here; the /display page (browser
# popup or native window) polls it every second. Server-mediated, so the display
# never depends on a window.opener reference and can never go stale.
display_html = ('<div class="pane left"><div style="color:#1a2030;font-size:3.5vw;font-size:clamp(20px,3.5vw,56px);'
                'padding:12vh 0;padding:clamp(40px,12vh,120px) 0;text-align:center;font-weight:700">'
                'Waiting for racing to start...</div></div><div class="pane right"></div>')

DISPLAY_PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Race Display</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#04060a;color:#fff;font-family:'Arial Narrow','Impact',system-ui,sans-serif;height:100vh;display:grid;grid-template-columns:1fr 1fr;grid-gap:0;gap:0;overflow:hidden;cursor:none}.pane{padding:3.5vw 3vw;padding:clamp(24px,3.5vw,60px) clamp(20px,3vw,52px);height:100vh;overflow:hidden}.left{border-right:2px solid #0d1520}.right{opacity:.82}</style>
</head><body>
<script>
var last='';
setInterval(function(){
  fetch('/display-content?t='+Date.now()).then(function(r){return r.text();}).then(function(h){
    if(h!==last){ last=h; document.body.innerHTML=h; }
  }).catch(function(){});
}, 1000);
</script>
</body></html>"""

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
            self._send_json({"dataDir": str(DATA_DIR), "migrated": migrated_this_run,
                             "version": APP_VERSION, "build": APP_BUILD,
                             "fullVersion": FULL_VERSION})
            migrated_this_run = False
            return

        if path_only == "/display":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DISPLAY_PAGE.encode("utf-8"))
            return

        if path_only == "/display-content":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(display_html.encode("utf-8"))
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

        if self.path == "/display-content":
            length = int(self.headers.get("Content-Length", 0))
            globals()["display_html"] = self.rfile.read(length).decode("utf-8", "replace")
            self._send_json({"ok": True})
            return

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
    """True if another Race Manager instance is already serving on our port.

    Runs on EVERY launch, so it has to fail fast when nothing is there.
    Two things matter:
      - 127.0.0.1, not "localhost". localhost resolves to IPv6 ::1 first and
        we bind IPv4 only, so the probe burned a full timeout on ::1 before
        retrying IPv4 - 2.05s of dead time on every single start-up.
      - a short timeout. This machine doesn't refuse the connection quickly,
        it just goes quiet, so the timeout IS the cost. A live local instance
        answers /ping in milliseconds, so 0.35s is plenty.
    """
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/ping", timeout=0.35) as r:
            return r.status == 200
    except Exception:
        return False


APP_URL = f"http://127.0.0.1:{PORT}/race-manager.html"


def prepare():
    """Migrate legacy data and make sure the data file exists."""
    migrate_legacy_data()  # copy (never move) pre-v10 data to the new home
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump({"version": 1, "seasons": [], "racers": [], "currentSeason": None}, f, indent=2)


def create_server():
    """Bind and return the HTTP server (raises OSError if the port is taken).
    127.0.0.1 (not all interfaces): keeps the app private to this machine and
    avoids the Windows Firewall prompt on first run."""
    socketserver.TCPServer.allow_reuse_address = True
    return socketserver.TCPServer(("127.0.0.1", PORT), RaceHandler)


def main():
    """Console mode - used by the zip distribution's launchers (bat/command)."""
    global server_ref

    if already_running():
        print("  Race Manager is already running - opening it in your browser.")
        try:
            webbrowser.open(APP_URL)
        except Exception:
            print(f"  Could not open a browser - go to {APP_URL} manually.")
        time.sleep(2)
        sys.exit(0)

    prepare()

    print("=" * 50)
    print(f"  TAMIYA RACE MANAGER v{FULL_VERSION}")
    print("=" * 50)
    print(f"  Starting on http://localhost:{PORT}")
    print(f"  Data file: {DATA_FILE}")
    print()
    print("  Opens automatically in your browser.")
    print("  Closes automatically when you close the tab.")
    print("  Press Ctrl+C to stop manually.")
    print("=" * 50)

    try:
        httpd = create_server()
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


if __name__ == "__main__":
    main()
