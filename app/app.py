#!/usr/bin/env python3
"""
Tamiya Race Manager - Desktop app entry point.

Runs the local server invisibly inside this process and shows the app in a
native window (pywebview / Edge WebView2). No console, no browser tab.
Closing the main window shuts everything down.

The zip distribution's launchers still use server.py directly (console +
browser mode); this file is what the installed TamiyaRaceManager.exe runs.

There is NO splash screen. Two attempts failed: PyInstaller's --splash
(v9.38) is Tcl/Tk and broke launches outright with 'Failed to load Tcl DLL',
and an HTML loading page shown in the window itself (v9.39) was visible for
~10ms - WebView2 can't paint until it has initialised, so it can't cover its
own initialisation.

Chasing that second failure turned up the real problem. Measured start-up
(the stamp() lines land in app.log) had a 2.05s hole in it that was NOT
WebView2 at all: already_running() probed "localhost", which resolves to
IPv6 ::1 first while the server binds IPv4 only, so every launch burned a
full timeout on a probe that could never succeed. Fixed in server.py. Now:

    0.02s  python + server import done
    0.07s  pywebview imported
    0.47s  already-running probe done
    0.48s  server bound, window created

With that gone the window is up in about half a second and the GUI loop
follows shortly after, so a splash isn't worth the machinery - a real one
would have to be a native Win32 window drawn before WebView2 starts.

If start-up ever feels slow again, read the stamps in app.log first rather
than guessing which stage is at fault; guessing got it wrong twice here.
"""
import os
import sys
import threading
import time
import webbrowser

# Start-up timing. T0 is as early as this module can observe; the process
# itself started somewhat before that (exe bootloader + interpreter init).
# Logged at each stage so slow launches can be diagnosed from app.log in
# the field instead of guessed at.
T0 = time.time()


def stamp(what):
    print(f"  [{time.time() - T0:5.2f}s] {what}")


import server

DISPLAY_URL = f"http://127.0.0.1:{server.PORT}/display"

# Kept OUTSIDE the Api class on purpose. pywebview walks the js_api object's
# attributes when it builds the JS bridge at start-up, and a webview Window
# stored there sends it into infinite recursion through window.native
# ("maximum recursion depth exceeded"), which wedges the whole app.
main_window = None

def window_geometry(want_w=1360, want_h=860):
    """Size and position for the main window: centred on the primary screen,
    shrunk to fit if the screen is smaller than the size we'd like.

    pywebview leaves placement to the OS, and Windows cascades new windows
    down-and-right from wherever the last one landed - so the app kept
    opening off-centre and part-way off smaller screens. Returns
    (width, height, x, y), or (want_w, want_h, None, None) if the screen
    can't be measured, in which case pywebview falls back to OS placement.

    Windows-only measurement. macOS centres new windows sensibly by itself,
    and ctypes.windll doesn't exist there - so return the fallback quietly
    rather than logging a failure on every Mac launch."""
    if os.name != "nt":
        return want_w, want_h, None, None
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
    # Send prints to a log file next to the data so field problems can be
    # diagnosed. On Windows a --noconsole build has no stdout at all, but a
    # macOS .app bundle DOES have one - it just goes nowhere. Checking
    # `frozen` as well means the Mac app actually writes a log; without it
    # a black-screen launch left nothing at all to diagnose.
    if getattr(sys, "frozen", False) or sys.stdout is None or sys.stderr is None:
        try:
            server.DATA_DIR.mkdir(parents=True, exist_ok=True)
            log = open(server.DATA_DIR / "app.log", "a", encoding="utf-8", buffering=1)
            sys.stdout = sys.stderr = log
            print(f"--- app start {time.strftime('%Y-%m-%d %H:%M:%S')} v{server.FULL_VERSION} ---")
        except Exception:
            import io
            sys.stdout = sys.stderr = io.StringIO()

    stamp("log open (python + server import done)")
    try:
        import webview
        stamp("pywebview imported")
    except Exception as e:
        # pywebview unavailable - fall back to console-style browser mode
        print(f"pywebview unavailable ({e}) - falling back to browser mode")
        server.main()
        return

    running = server.already_running()
    stamp("already-running probe done")
    if running:
        # Another instance owns the server - just show a window onto it
        w2, h2, x2, y2 = window_geometry()
        webview.create_window("Tamiya Race Manager", server.APP_URL,
                              width=w2, height=h2, x=x2, y=y2,
                              min_size=(900, 600))
        webview.start()
        return

    # Server first, then the window: starting it costs ~0.01s and the window
    # can then load the app directly. No splash - see the start-up note at
    # the top of this file.
    server.prepare()
    try:
        httpd = server.create_server()
    except OSError:
        win_w, win_h, win_x, win_y = window_geometry(560, 240)
        webview.create_window(
            "Tamiya Race Manager",
            html="<body style='background:#080b0f;color:#eef4ff;font-family:sans-serif'>"
                 "<h2 style='padding:24px'>Port 8765 is in use by "
                 "another program.<br><br>Close that program (or restart the computer) "
                 "and try again.</h2></body>",
            width=win_w, height=win_h, x=win_x, y=win_y)
        webview.start()
        return

    server.server_ref = httpd
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    # NO WATCHDOG in the desktop app. Closing the window is the exit route
    # (main_win.events.closed -> os._exit), so the heartbeat has nothing to
    # tell us that the window itself does not. It only ever added risk: the
    # WebView throttles background timers, so an app left open but untouched
    # during a race night stopped pinging often enough and the watchdog
    # killed it mid-event. Browser mode still runs it - see server.main() -
    # because there a closed tab is genuinely undetectable otherwise.
    print(f"Server on port {server.PORT}; data file: {server.DATA_FILE}")
    stamp("server up, creating window")

    api = Api()
    try:
        win_w, win_h, win_x, win_y = window_geometry()
        main_win = webview.create_window(
            "Tamiya Race Manager", server.APP_URL, js_api=api,
            width=win_w, height=win_h, x=win_x, y=win_y,
            min_size=(900, 600), background_color="#080b0f")
        stamp("window created")
        global main_window
        main_window = main_win
        # Coordinator closes the main window -> the whole app closes
        main_win.events.closed += lambda: os._exit(0)
        webview.start()
    except Exception as e:
        # WebView2 runtime missing or GUI failed - browser fallback keeps
        # race night running rather than dying on the spot.
        print(f"Native window failed ({e}) - falling back to the browser")
        try:
            webbrowser.open(server.APP_URL)
        except Exception:
            pass
        while True:
            time.sleep(60)

    os._exit(0)


if __name__ == "__main__":
    run()
