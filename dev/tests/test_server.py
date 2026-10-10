#!/usr/bin/env python3
"""
Tamiya Race Manager - server and data-safety tests.

Everything here can run unattended. It does NOT need a browser, and it never
touches real race data: it starts the app's own server against a throwaway
directory via TAMIYA_DATA_DIR.

Run it with:   python dev/tests/test_server.py

Each test states what it is protecting against, because a test whose purpose
nobody remembers gets deleted the first time it is inconvenient.
"""
import json
import os
import shutil
import socket
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "app"))

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  -> ' + detail) if detail else ''}")
    return ok


def req(base, path, data=None, timeout=5):
    """Returns (status, body, seconds). Never raises."""
    t0 = time.time()
    try:
        r = urllib.request.Request(
            base + path, data=data,
            headers={"Content-Type": "application/json"} if data else {})
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, b"", time.time() - t0
    except Exception as e:
        return "ERR:" + type(e).__name__, b"", time.time() - t0


def main():
    tmp = Path(tempfile.mkdtemp(prefix="trm-test-"))
    os.environ["TAMIYA_DATA_DIR"] = str(tmp / "data")
    os.environ["TAMIYA_ARCHIVE_DIR"] = str(tmp / "arch")
    (tmp / "data").mkdir(parents=True)

    # A realistic file, not an empty one: size matters for the timing tests.
    seed = {"version": 1, "currentSeason": "s1", "racers":
            [{"id": f"r{i:05d}", "name": f"Racer {i}", "isJunior": i % 3 == 0}
             for i in range(90)],
            "seasons": [{"id": "s1", "name": "Test", "closed": False, "events":
                         [{"id": f"e{i:05d}", "date": "01/01/2026", "classKey": "box",
                           "results": [{"rosterId": f"r{j:05d}", "name": f"Racer {j}",
                                        "position": j + 1, "points": max(0, 10 - j)}
                                       for j in range(20)]} for i in range(47)]}]}
    (tmp / "data" / "racedata.json").write_text(json.dumps(seed), encoding="utf-8")

    import server
    httpd = server.create_server()
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    time.sleep(0.4)
    base = f"http://127.0.0.1:{server.PORT}"
    print(f"\nTamiya Race Manager test server on {base}")
    print(f"scratch: {tmp}\n")

    # ---------------------------------------------------------------- server
    print("SERVER - one bad client must not stop race night")
    check("server is threaded",
          isinstance(httpd, __import__("socketserver").ThreadingMixIn),
          type(httpd).__name__)
    check("handler has a socket timeout", server.RaceHandler.timeout is not None,
          f"{server.RaceHandler.timeout}s")

    st, _, _ = req(base, "/display-content")
    check("display feed answers normally", st == 200)

    # The 2026-10-10 bug: a client that connects then goes silent used to wedge
    # the single-threaded server forever, blanking the display AND freezing the
    # main window so the podium never appeared.
    stalled = []
    for _ in range(5):
        s = socket.create_connection(("127.0.0.1", server.PORT))
        s.sendall(b"GET /display-content HTTP/1.0\r\n")   # headers never finished
        stalled.append(s)
    st, _, el = req(base, "/display-content")
    check("5 stalled clients do not block the display feed", st == 200 and el < 1.0,
          f"{el:.2f}s")
    st, _, el = req(base, "/info")
    check("5 stalled clients do not block the main app", st == 200 and el < 1.0,
          f"{el:.2f}s")
    for s in stalled:
        try:
            s.close()
        except Exception:
            pass

    # --------------------------------------------------------------- display
    print("\nDISPLAY PAGE - must never go blank in front of a room")
    st, body, _ = req(base, "/display")
    page = body.decode("utf-8", "replace")
    check("serves 200", st == 200)
    check("renders into #stage, not document.body",
          'id="stage"' in page and "document.body.innerHTML" not in page,
          "overwriting body destroys the page's own <script>")
    check("seeded with a waiting message", "Waiting for racing to start" in page,
          "so a failed FIRST poll is not a black screen")
    check("has an in-flight guard", "if (busy) return" in page)
    check("has a request watchdog", "setTimeout" in page and "4000" in page)
    check("watchdog clears the flag itself, not via the promise",
          "if (mine === inflight) busy = false" in page,
          "AbortController is absent on Safari 11 / macOS 10.13")
    check("refuses to paint an empty body", "if (h && h !== last)" in page)

    # ----------------------------------------------------------- data safety
    print("\nDATA SAFETY - the club's only database")
    before = json.loads((tmp / "data" / "racedata.json").read_text(encoding="utf-8"))

    errors = []

    def saver(i):
        d = dict(before)
        d["_writer"] = i
        st, _, _ = req(base, "/save", data=json.dumps(d).encode(), timeout=20)
        if st != 200:
            errors.append((i, st))

    ths = [threading.Thread(target=saver, args=(i,)) for i in range(20)]
    [t.start() for t in ths]
    [t.join() for t in ths]
    check("20 concurrent saves all succeed", not errors, str(errors[:3]))
    try:
        after = json.loads((tmp / "data" / "racedata.json").read_text(encoding="utf-8"))
        ok = (len(after["racers"]) == len(before["racers"])
              and len(after["seasons"][0]["events"]) == len(before["seasons"][0]["events"]))
        check("data file is still valid and complete", ok,
              f"{len(after['racers'])} racers, {len(after['seasons'][0]['events'])} events")
    except Exception as e:
        check("data file is still valid and complete", False, str(e))

    leftovers = list((tmp / "data").glob("racedata.tmp*"))
    check("no temp files left behind", not leftovers, str([p.name for p in leftovers]))
    check("a write lock exists", hasattr(server, "_write_lock"),
          "threading without one can leave a half-written file as the only DB")

    # --------------------------------------------------------------- archive
    print("\nBACKUP - the safety nets")
    r1 = server.archive_snapshot(reason="test")
    check("archive writes a snapshot", isinstance(r1, str) and not r1.startswith("!"),
          Path(str(r1)).name if r1 else str(r1))
    r2 = server.archive_snapshot(reason="test")
    check("unchanged data does NOT add a second file", r2 is None,
          "every file in the folder should be a real change")
    p = tmp / "data" / "racedata.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["_night"] = 2
    p.write_text(json.dumps(d), encoding="utf-8")
    time.sleep(1.1)
    r3 = server.archive_snapshot(reason="test")
    check("a real change DOES add a file",
          isinstance(r3, str) and not r3.startswith("!"))
    check("archive folder explains itself",
          (Path(os.environ["TAMIYA_ARCHIVE_DIR"]) / "README-what-these-files-are.txt").exists())
    check("system drive is never a backup target",
          all(dr["letter"].upper() != (os.environ.get("SystemDrive") or "C:").upper()
              for dr in server.removable_drives()),
          "backing up onto the disk it already lives on is not a backup")

    httpd.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'=' * 60}")
    print(f"  {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        print("  FAILED: " + ", ".join(FAIL))
    print(f"{'=' * 60}")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
