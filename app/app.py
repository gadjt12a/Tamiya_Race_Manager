#!/usr/bin/env python3
"""
Tamiya Race Manager - Desktop app entry point.

Runs the local server invisibly inside this process and shows the app in a
native window (pywebview / Edge WebView2). No console, no browser tab.
Closing the main window shuts everything down.

The zip distribution's launchers still use server.py directly (console +
browser mode); this file is what the installed TamiyaRaceManager.exe runs.
"""
import os
import sys
import threading
import time
import webbrowser

import server

DISPLAY_URL = f"http://127.0.0.1:{server.PORT}/display"

# Kept OUTSIDE the Api class on purpose. pywebview walks the js_api object's
# attributes when it builds the JS bridge at start-up, and a webview Window
# stored there sends it into infinite recursion through window.native
# ("maximum recursion depth exceeded"), which wedges the whole app.
main_window = None

# Shown the instant the window opens, while the server starts behind it.
# Self-contained (no server, no files, no Tcl/Tk) - it has to render before
# anything else exists. Colours match the app's own theme.
LOADING_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  html,body{height:100%;margin:0;background:#080b0f;color:#eef4ff;
    font-family:'Segoe UI',sans-serif;overflow:hidden}
  .wrap{height:100%;display:flex;flex-direction:column;
    align-items:center;justify-content:center;gap:18px}
  .flag{font-size:64px;line-height:1}
  h1{font-family:'Arial Narrow','Impact',sans-serif;font-size:34px;font-weight:800;
    letter-spacing:.08em;text-transform:uppercase;color:#e8a020;margin:0}
  p{color:#8aa8c4;font-size:14px;letter-spacing:.14em;text-transform:uppercase;margin:0}
  .bar{width:220px;height:3px;border-radius:2px;background:#1e2a3c;overflow:hidden}
  .bar i{display:block;width:40%;height:100%;background:#e8a020;
    animation:slide 1.1s ease-in-out infinite}
  @keyframes slide{0%{transform:translateX(-100%)}100%{transform:translateX(250%)}}
</style></head><body>
  <div class="wrap">
    <div class="flag">&#127937;</div>
    <h1>Tamiya Race Manager</h1>
    <div class="bar"><i></i></div>
    <p>Loading&hellip;</p>
  </div>
</body></html>
"""


def window_geometry(want_w=1360, want_h=860):
    """Size and position for the main window: centred on the primary screen,
    shrunk to fit if the screen is smaller than the size we'd like.

    pywebview leaves placement to the OS, and Windows cascades new windows
    down-and-right from wherever the last one landed - so the app kept
    opening off-centre and part-way off smaller screens. Returns
    (width, height, x, y), or (want_w, want_h, None, None) if the screen
    can't be measured, in which case pywebview falls back to OS placement."""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        if screen_w <= 0 or screen_h <= 0:
            return want_w, want_h, None, None
        # Leave a margin so the window never sits edge-to-edge or under the taskbar
        w = min(want_w, screen_w - 80)
        h = min(want_h, screen_h - 120)
        return w, h, max(0, (screen_w - w) // 2), max(0, (screen_h - h) // 2)
    except Exception as e:
        print(f"window_geometry failed ({e}) - letting the OS place the window")
        return want_w, want_h, None, None


class Api:
    """Called from the app's JavaScript via window.pywebview.api"""

    def __init__(self):
        self.display_window = None

    def toggle_fullscreen(self):
        """Full-screen the main app window (Full Screen button / F11)."""
        try:
            if main_window is not None:
                main_window.toggle_fullscreen()
                return True
        except Exception as e:
            print(f"toggle_fullscreen failed: {e}")
        return False

    def open_display(self):
        """Open (or re-open) the second-screen display as a native window -
        full-screen on the second monitor when one is present."""
        try:
            if self.display_window is not None:
                try:
                    self.display_window.destroy()
                except Exception:
                    pass
                self.display_window = None
            import webview
            screens = webview.screens
            if len(screens) > 1:
                self.display_window = webview.create_window(
                    "Race Display", DISPLAY_URL, screen=screens[1], fullscreen=True)
            else:
                self.display_window = webview.create_window(
                    "Race Display", DISPLAY_URL, width=1280, height=720)
            return True
        except Exception as e:
            print(f"open_display failed: {e}")
            return False


def run():
    # Windowed (no-console) builds have no stdout - send prints to a log file
    # next to the data so field problems can be diagnosed.
    if sys.stdout is None or sys.stderr is None:
        try:
            server.DATA_DIR.mkdir(parents=True, exist_ok=True)
            log = open(server.DATA_DIR / "app.log", "a", encoding="utf-8", buffering=1)
            sys.stdout = sys.stderr = log
            print(f"--- app start {time.strftime('%Y-%m-%d %H:%M:%S')} v{server.FULL_VERSION} ---")
        except Exception:
            import io
            sys.stdout = sys.stderr = io.StringIO()

    try:
        import webview
    except Exception as e:
        # pywebview unavailable - fall back to console-style browser mode
        print(f"pywebview unavailable ({e}) - falling back to browser mode")
        server.main()
        return

    if server.already_running():
        # Another instance owns the server - just show a window onto it
        w2, h2, x2, y2 = window_geometry()
        webview.create_window("Tamiya Race Manager", server.APP_URL,
                              width=w2, height=h2, x=x2, y=y2,
                              min_size=(900, 600))
        webview.start()
        return

    api = Api()
    try:
        # The window opens IMMEDIATELY on the loading screen, before any of
        # the slow work (data migration, server bind, first page load), so a
        # double-click gives instant feedback. boot() below then swaps it to
        # the real app. This replaces the v9.38 Tcl/Tk splash, which broke
        # launches outright - see close_splash().
        win_w, win_h, win_x, win_y = window_geometry()
        main_win = webview.create_window(
            "Tamiya Race Manager", html=LOADING_HTML, js_api=api,
            width=win_w, height=win_h, x=win_x, y=win_y,
            min_size=(900, 600), background_color="#080b0f")
        global main_window
        main_window = main_win
        # Coordinator closes the main window -> the whole app closes
        main_win.events.closed += lambda: os._exit(0)

        def boot(window):
            """Runs once the window is on screen: do the slow start-up work,
            then swap the loading screen for the real app. pywebview passes
            the window in as the argument - it must be accepted."""
            server.prepare()
            try:
                httpd = server.create_server()
            except OSError:
                main_win.load_html(
                    "<body style='background:#080b0f;color:#eef4ff;font-family:sans-serif'>"
                    "<h2 style='padding:24px'>Port 8765 is in use by another program."
                    "<br><br>Close that program (or restart the computer) "
                    "and try again.</h2></body>")
                return
            server.server_ref = httpd
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            # Watchdog still runs as a fallback, but window-close is the primary exit
            threading.Thread(target=server.watchdog, daemon=True).start()
            print(f"Server on port {server.PORT}; data file: {server.DATA_FILE}")
            main_win.load_url(server.APP_URL)

        webview.start(boot, main_win)
    except Exception as e:
        # WebView2 runtime missing or GUI failed - browser fallback keeps
        # race night running rather than dying on the spot.
        print(f"Native window failed ({e}) - falling back to the browser")
        try:
            server.prepare()
            httpd = server.create_server()
            server.server_ref = httpd
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            threading.Thread(target=server.watchdog, daemon=True).start()
        except Exception as e2:
            print(f"Server start failed in browser fallback: {e2}")
        try:
            webbrowser.open(server.APP_URL)
        except Exception:
            pass
        while True:
            time.sleep(60)

    os._exit(0)


if __name__ == "__main__":
    run()
