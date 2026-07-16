#!/usr/bin/env python3
"""
Tamiya Race Manager — Local Server
Serves the app, handles data file read/write, and shuts down when the browser tab closes.
"""
import http.server
import json
import os
import shutil
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

PORT = 8765
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "racedata.json"
BACKUP_DIR = BASE_DIR / "data" / "backups"
BACKUP_KEEP = 14  # daily backups retained


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
last_ping = time.time()
server_ref = None

def watchdog():
    """Background thread — shuts down server if browser tab closes.
    Sleep-tolerant: if the wall clock jumps (laptop lid closed / machine slept),
    the browser never had a chance to ping, so reset the timer instead of
    killing the server out from under an open tab."""
    global last_ping
    time.sleep(10)  # grace period on startup
    last_check = time.time()
    while True:
        time.sleep(3)
        now = time.time()
        if now - last_check > 30:  # slept far past our 3s interval
            last_ping = now  # give the browser a fresh window to resume pinging
        last_check = now
        if now - last_ping > HEARTBEAT_TIMEOUT:
            print("\n  Browser tab closed — shutting down. Goodbye!")
            if server_ref:
                threading.Thread(target=server_ref.shutdown, daemon=True).start()
            os._exit(0)


class RaceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        global last_ping
        if self.path == "/ping":
            last_ping = time.time()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return
        super().do_GET()

    def do_POST(self):
        global last_ping
        last_ping = time.time()

        if self.path == "/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                DATA_FILE.parent.mkdir(exist_ok=True)
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
            print("\n  Shutdown requested — stopping server. Goodbye!")
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


if __name__ == "__main__":
    DATA_FILE.parent.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump({"version": 1, "seasons": [], "racers": [], "currentSeason": None}, f, indent=2)

    print("=" * 50)
    print("  TAMIYA RACE MANAGER")
    print("=" * 50)
    print(f"  Starting on http://localhost:{PORT}")
    print(f"  Data file: {DATA_FILE}")
    print()
    print("  Opens automatically in your browser.")
    print("  Closes automatically when you close the tab.")
    print("  Press Ctrl+C to stop manually.")
    print("=" * 50)

    webbrowser.open(f"http://localhost:{PORT}/race-manager.html")

    with socketserver.TCPServer(("", PORT), RaceHandler) as httpd:
        server_ref = httpd
        t = threading.Thread(target=watchdog, daemon=True)
        t.start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped. Goodbye!")
