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


def close_splash():
    """Close the PyInstaller boot splash, if this build has one.

    Currently a no-op: the splash was dropped in v9.39 because PyInstaller
    implements it in Tcl/Tk, which broke launches with 'Failed to load Tcl
    DLL' errors. The onedir build starts fast enough not to need it. Hooks
    are left in place so a future splash can be closed at the right moment."""
    try:
        import pyi_splash
        pyi_splash.close()
    except Exception:
        pass


class Api:
    """Called from the app's JavaScript via window.pywebview.api"""

    def __init__(self):
        self.display_window = None

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
            print(f"--- app start {time.strftime('%Y-%m-%d %H:%M:%S')} v{server.APP_VERSION} ---")
        except Exception:
            import io
            sys.stdout = sys.stderr = io.StringIO()

    try:
        import webview
    except Exception as e:
        # pywebview unavailable - fall back to console-style browser mode
        print(f"pywebview unavailable ({e}) - falling back to browser mode")
        close_splash()
        server.main()
        return

    if server.already_running():
        # Another instance owns the server - just show a window onto it
        w = webview.create_window("Tamiya Race Manager", server.APP_URL,
                                  width=1360, height=860, min_size=(900, 600))
        w.events.shown += close_splash
        webview.start()
        return

    server.prepare()
    try:
        httpd = server.create_server()
    except OSError:
        close_splash()
        webview.create_window(
            "Tamiya Race Manager",
            html="<h2 style='font-family:sans-serif;padding:24px'>Port 8765 is in use by "
                 "another program.<br><br>Close that program (or restart the computer) "
                 "and try again.</h2>",
            width=560, height=240)
        webview.start()
        return

    server.server_ref = httpd
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    # Watchdog still runs as a fallback, but window-close is the primary exit
    threading.Thread(target=server.watchdog, daemon=True).start()
    print(f"Server on port {server.PORT}; data file: {server.DATA_FILE}")

    api = Api()
    try:
        main_win = webview.create_window(
            "Tamiya Race Manager", server.APP_URL, js_api=api,
            width=1360, height=860, min_size=(900, 600))
        # Splash stays up until the real window is on screen
        main_win.events.shown += close_splash
        # Coordinator closes the main window -> the whole app closes
        main_win.events.closed += lambda: os._exit(0)
        webview.start()
    except Exception as e:
        # WebView2 runtime missing or GUI failed - browser fallback keeps
        # race night running rather than dying on the spot.
        print(f"Native window failed ({e}) - falling back to the browser")
        close_splash()
        try:
            webbrowser.open(server.APP_URL)
        except Exception:
            pass
        while True:
            time.sleep(60)

    os._exit(0)


if __name__ == "__main__":
    run()
