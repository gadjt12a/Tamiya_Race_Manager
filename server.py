#!/usr/bin/env python3
"""
Tamiya Race Manager — Local Server
Serves the app, handles data file read/write, and shuts down when the browser tab closes.
"""
import http.server
import json
import os
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

PORT = 8765
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "racedata.json"

# ── Heartbeat watchdog ─────────────────────────────────────────────────────────
# The browser page sends a /ping every 5 seconds while open.
# If we don't receive a ping for 12 seconds, the tab has been closed → shut down.
HEARTBEAT_TIMEOUT = 12
last_ping = time.time()
server_ref = None

def watchdog():
    """Background thread — shuts down server if browser tab closes."""
    time.sleep(10)  # grace period on startup
    while True:
        time.sleep(3)
        if time.time() - last_ping > HEARTBEAT_TIMEOUT:
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
                with open(DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
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
