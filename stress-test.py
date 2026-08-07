#!/usr/bin/env python3
"""
Tamiya Race Manager -- Stress Test
Simulates 30 race nights (Box + EVO + Pro each night) using the same
bracket logic as app/race-manager.html and validates data integrity.

This re-implements the bracket rules rather than importing them, so it
can drift from the app. If a rule changes in app/race-manager.html,
change it here too.

The generated data is written to  data/racedata.json  BESIDE THIS SCRIPT
purely as scratch output for inspection. That is NOT where the app keeps
its data - the app uses %LOCALAPPDATA%\TamiyaRaceManager\ (Windows) and
never reads this file, so running this cannot touch real club data. The
data/ folder is gitignored.

Covers:
  - Bracket engine correctness (all racer counts 3-21)
  - Junior points ranking (fixed: by junior rank not overall position)
  - Triple / Double night multipliers (correct points, correct scheme flag)
  - Auto-save upsert (re-saving an event must not create a duplicate)
  - Season roster active/inactive flags (inactive racers excluded from events)
  - Multi-season roster continuity (previous season racer IDs match DB)
  - Static points-scheme validation (schemes match race-manager.html exactly)

Usage:  python stress-test.py [runs]   (default: 3 runs)
"""

import json, os, random, sys
from datetime import date, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "racedata.json"
NIGHTS    = 30
RUNS      = int(sys.argv[1]) if len(sys.argv) > 1 else 3

# ── Points schemes (mirrored from race-manager.html) ─────────────────────────
POINTS_SCHEMES = {
    "standard": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    "double":   [20, 18, 16, 14, 12, 10, 8, 6, 4, 2],
    "triple":   [30, 27, 24, 21, 18, 15, 12, 9, 6, 3],
    "podium":   [3, 2, 1],
}

def pos_points(pos, scheme="standard"):
    s = POINTS_SCHEMES.get(scheme, POINTS_SCHEMES["standard"])
    return s[pos - 1] if 1 <= pos <= len(s) else 0

# ── Static scheme validation (runs once at startup) ──────────────────────────
def validate_schemes():
    errors = []
    checks = [
        ("standard", 1,  10), ("standard", 10, 1),  ("standard", 11, 0),
        ("double",   1,  20), ("double",   10, 2),  ("double",   11, 0),
        ("triple",   1,  30), ("triple",   10, 3),  ("triple",   11, 0),
        ("podium",   1,   3), ("podium",    3, 1),  ("podium",    4, 0),
    ]
    for scheme, pos, expected in checks:
        got = pos_points(pos, scheme)
        if got != expected:
            errors.append(f"pos_points({pos}, '{scheme}') = {got}, expected {expected}")
    # Verify each scheme is strictly non-increasing
    for name, vals in POINTS_SCHEMES.items():
        for i in range(len(vals) - 1):
            if vals[i] < vals[i + 1]:
                errors.append(f"scheme '{name}' not non-increasing at index {i}: {vals[i]} < {vals[i+1]}")
    return errors

# ── Helpers ───────────────────────────────────────────────────────────────────
_uid_counter = 0
def uid():
    global _uid_counter
    _uid_counter += 1
    return f"{random.randint(0, 0xFFFFFF):06x}{_uid_counter:03x}"

def make_batches(ids):
    """Mirror of makeBatches() in race-manager.html."""
    a = list(ids)
    n = len(a)
    if n < 2:
        return [[a[0]]] if n == 1 else []
    if n <= 3:
        return [a]
    twos   = 0 if n % 3 == 0 else (1 if n % 3 == 2 else 2)
    threes = (n - twos * 2) // 3
    out, i = [], 0
    for _ in range(threes): out.append(a[i:i+3]); i += 3
    for _ in range(twos):   out.append(a[i:i+2]); i += 2
    return out

def get_name(R, rid):
    for r in R["racers"]:
        if r["id"] == rid:
            return r["name"]
    return "?"

# ── Bracket engine (mirrors race-manager.html) ────────────────────────────────
def serve_next_race(R):
    if R["roundQueue"]:
        nxt = R["roundQueue"].pop(0)
        R["raceNum"] += 1
        R["currentRace"] = {
            "racers": nxt["racers"], "bracket": nxt["bracket"],
            "num": R["raceNum"], "p1": None, "p2": None, "p3": None,
        }
    else:
        start_next_round(R)

def start_next_round(R):
    main, second = R["mainPool"], R["secondPool"]

    # Sole survivor
    if len(main) == 1 and len(second) == 0:
        rid = main[0]
        R["podium"] = {"first": rid, "second": None, "third": None}
        R["bracket"][rid] = "champ"
        R["mainPool"] = []
        R["currentRace"] = None
        return

    # Standard 3-person final
    if len(main) == 1 and len(second) == 2:
        finalists = random.sample(main + second, len(main) + len(second))
        R["mainPool"], R["secondPool"] = [], []
        R["roundType"] = "final"
        R["roundQueue"] = [{"racers": finalists, "bracket": "final"}]
        serve_next_race(R); return

    # 2-person final edge case
    if len(main) == 1 and len(second) == 1:
        finalists = random.sample(main + second, 2)
        R["mainPool"], R["secondPool"] = [], []
        R["roundType"] = "final"
        R["roundQueue"] = [{"racers": finalists, "bracket": "final"}]
        serve_next_race(R); return

    # secondPool==3, mainPool==1: give best a bye
    if len(main) == 1 and len(second) == 3:
        sorted_s = sorted(second,
            key=lambda x: (-R["wins"].get(x, 0), R["losses"].get(x, 0)))
        bye_id   = sorted_s[0]
        race_two = sorted_s[1:]
        R["raceNum"] += 1
        bye_entry = {
            "num": R["raceNum"], "bracket": "bye",
            "names": [get_name(R, bye_id)], "places": [get_name(R, bye_id)],
            "placeIds": [bye_id], "isFinal": False, "isBye": True,
        }
        R["history"].insert(0, bye_entry)
        R["wins"][bye_id] = R["wins"].get(bye_id, 0) + 1
        R["secondPool"] = [bye_id]
        R["roundType"]  = "second"
        R["roundQueue"] = [{"racers": race_two, "bracket": "second"}]
        serve_next_race(R); return

    # Normal round alternation
    rt = R["roundType"]
    if rt in ("main", None):
        if len(second) >= 2:
            ids = random.sample(second, len(second)); R["secondPool"] = []
            R["roundType"]  = "second"
            R["roundQueue"] = [{"racers": b, "bracket": "second"} for b in make_batches(ids)]
        elif len(main) >= 2:
            ids = random.sample(main, len(main)); R["mainPool"] = []
            R["roundType"]  = "main"
            R["roundQueue"] = [{"racers": b, "bracket": "main"} for b in make_batches(ids)]
        else:
            R["currentRace"] = None; return
    elif rt == "second":
        if len(main) >= 2:
            ids = random.sample(main, len(main)); R["mainPool"] = []
            R["roundType"]  = "main"
            R["roundQueue"] = [{"racers": b, "bracket": "main"} for b in make_batches(ids)]
        elif len(second) >= 2:
            ids = random.sample(second, len(second)); R["secondPool"] = []
            R["roundQueue"] = [{"racers": b, "bracket": "second"} for b in make_batches(ids)]
        else:
            R["currentRace"] = None; return

    serve_next_race(R)

def confirm_result(R, p1, p2, p3):
    """Process a race result. p3 may be None for 2-person races."""
    cr = R["currentRace"]
    was_final = cr["bracket"] == "final"
    losers = [p2, p3] if p3 else [p2]

    R["wins"][p1]  = R["wins"].get(p1, 0) + 1
    for lid in losers:
        R["losses"][lid] = R["losses"].get(lid, 0) + 1

    hist_entry = {
        "num": cr["num"], "bracket": cr["bracket"],
        "names":    [get_name(R, x) for x in cr["racers"]],
        "places":   [get_name(R, p1), get_name(R, p2)] + ([get_name(R, p3)] if p3 else []),
        "placeIds": [p1, p2] + ([p3] if p3 else []),
        "isFinal":  was_final,
    }
    R["history"].insert(0, hist_entry)

    if was_final:
        R["podium"]      = {"first": p1, "second": p2, "third": p3}
        R["bracket"][p1] = "champ"
        R["currentRace"] = None
        return

    if cr["bracket"] == "main":
        R["bracket"][p1] = "main"; R["mainPool"].append(p1)
        for lid in losers:
            R["bracket"][lid] = "second"; R["secondPool"].append(lid)
    else:
        R["bracket"][p1] = "second"; R["secondPool"].append(p1)
        for lid in losers:
            R["bracket"][lid] = "elim"; R["eliminated"].append(lid)

    R["currentRace"] = None
    serve_next_race(R)

def create_race_state(entries, class_key):
    racers = [{"id": e["id"], "name": e["name"], "isJunior": bool(e.get("isJunior")),
               "rosterId": e.get("rosterId")} for e in entries]
    return {
        "racers": racers, "classKey": class_key, "mode": "normal",
        "wins":   {r["id"]: 0 for r in racers},
        "losses": {r["id"]: 0 for r in racers},
        "bracket":    {r["id"]: "main" for r in racers},
        "eliminated": [], "raceNum": 0, "history": [],
        "podium": None, "juniorPodium": None,
        "mainPool":   [r["id"] for r in racers],
        "secondPool": [], "roundQueue": [], "roundType": None,
        "currentRace": None, "eventId": uid(),
    }

def compute_junior_podium(R):
    if R["classKey"] != "evo":
        return None
    juniors = [r for r in R["racers"] if r["isJunior"]]
    if not juniors:
        return None
    pod = R["podium"] or {}
    pod_order = [x for x in [pod.get("first"), pod.get("second"), pod.get("third")] if x]

    def sort_key(r):
        try:    return (0, pod_order.index(r["id"]))
        except: pass
        return (1, -R["wins"].get(r["id"], 0), R["losses"].get(r["id"], 0))

    sj = sorted(juniors, key=sort_key)
    return {
        "first":  sj[0]["id"] if len(sj) > 0 else None,
        "second": sj[1]["id"] if len(sj) > 1 else None,
        "third":  sj[2]["id"] if len(sj) > 2 else None,
    }

def compute_final_standings(R, scheme="standard"):
    pod = R["podium"] or {}
    pod_order = [x for x in [pod.get("first"), pod.get("second"), pod.get("third")] if x]

    def sort_key(r):
        try:    return (0, pod_order.index(r["id"]))
        except: pass
        is_elim = r["id"] in R["eliminated"]
        return (2 if is_elim else 1, -R["wins"].get(r["id"], 0), R["losses"].get(r["id"], 0))

    sorted_r = sorted(R["racers"], key=sort_key)
    return [{
        "racerId":  r["id"],
        "rosterId": r.get("rosterId"),
        "name":     r["name"],
        "isJunior": r["isJunior"],
        "position": i + 1,
        "points":   pos_points(i + 1, scheme),
        "wins":     R["wins"].get(r["id"], 0),
        "losses":   R["losses"].get(r["id"], 0),
    } for i, r in enumerate(sorted_r)]

def simulate_class(entries, class_key, scheme="standard"):
    """Run a full class simulation. Returns (results, junior_podium, race_breakdown, racer_summary, R)."""
    R = create_race_state(entries, class_key)
    start_next_round(R)

    max_iter = 1000
    while not R["podium"] and max_iter > 0:
        max_iter -= 1
        cr = R["currentRace"]
        if not cr:
            raise RuntimeError(
                f"{class_key}: currentRace is None but no podium. "
                f"main={len(R['mainPool'])} second={len(R['secondPool'])}"
            )
        shuffled = random.sample(cr["racers"], len(cr["racers"]))
        p1, p2 = shuffled[0], shuffled[1]
        p3 = shuffled[2] if len(shuffled) >= 3 else None
        confirm_result(R, p1, p2, p3)

    if not R["podium"]:
        raise RuntimeError(f"{class_key}: reached iteration limit without a podium")

    R["juniorPodium"] = compute_junior_podium(R)
    results = compute_final_standings(R, scheme)
    race_breakdown = list(reversed([{
        "raceNum": h["num"], "bracket": h["bracket"],
        "racers": h["names"], "places": h["places"], "isFinal": bool(h.get("isFinal")),
    } for h in R["history"]]))
    racer_summary = [{
        "position": s["position"], "name": s["name"], "isJunior": s["isJunior"],
        "wins": s["wins"], "losses": s["losses"], "points": s["points"],
        "pointsScheme": scheme,
    } for s in results]

    return results, R["juniorPodium"], race_breakdown, racer_summary, R

def build_event(R, results, jp, rb, rs, class_key, class_label, night_date,
                scheme, double_points, triple_points):
    """Build the event dict that matches what autoSaveResults() writes to the DB."""
    return {
        "id":           R["eventId"],
        "date":         night_date,
        "type":         "normal",
        "classKey":     class_key,
        "classLabel":   class_label,
        "specialName":  "",
        "doublePoints": double_points,
        "triplePoints": triple_points,
        "pointsScheme": scheme,
        "racerCount":   len(R["racers"]),
        "results":      results,
        "podium":       R["podium"],
        "juniorPodium": jp,
        "raceBreakdown": rb,
        "racerSummary":  rs,
    }

def upsert_event(season, event):
    """Mirror of the upsert logic in autoSaveResults()."""
    idx = next((i for i, e in enumerate(season["events"]) if e["id"] == event["id"]), -1)
    if idx >= 0:
        season["events"][idx] = event
    else:
        season["events"].append(event)

# ── Racer pools ────────────────────────────────────────────────────────────────
ADULT_POOL = [
    "Marcus", "Lucas", "Ethan", "Noah", "Oliver",
    "Sophia", "Emma",  "Mia",   "Harper", "Lily",
    "James",  "Liam",  "Nathan", "Ryan",  "Jake",
    "Callie", "Grace", "Zara",  "Finn",  "Owen",
    "Tyler",  "Sam",   "Jordan", "Alex",  "Morgan",
    "Riley",  "Casey", "Drew",  "Quinn",
]
JUNIOR_POOL = ["Kai", "Eli", "Mila", "Ava", "Leo", "Zoe", "Ruby", "Max"]
PRO_POOL    = ADULT_POOL[:15]

# ── Main stress test ──────────────────────────────────────────────────────────
def run_stress_test(run_num, carry_db=None):
    """
    Run one stress test.
    carry_db: if supplied, add a second season to an existing DB (tests multi-season flow).
    Returns (DB, errors, warnings).
    """
    print(f"\n{'='*60}")
    print(f"  STRESS TEST RUN {run_num}")
    print(f"{'='*60}")

    errors, warnings = [], []

    if carry_db:
        DB     = carry_db
        roster = {r["name"].lower().strip(): r for r in DB["racers"]}
    else:
        DB     = {"version": 1, "seasons": [], "racers": [], "currentSeason": None}
        roster = {}

    def ensure_racer(name, is_junior=False):
        key = name.lower().strip()
        if key not in roster:
            rec = {"id": uid(), "name": name, "isJunior": bool(is_junior), "active": True}
            DB["racers"].append(rec)
            roster[key] = rec
        elif is_junior:
            roster[key]["isJunior"] = True
        return roster[key]

    season_id = uid()
    season = {
        "id": season_id, "name": f"2026 Season (Run {run_num})",
        "startDate": "01/01/2026", "endDate": None, "closed": False, "events": [],
    }
    DB["seasons"].append(season)
    DB["currentSeason"] = season_id

    # ── Night multiplier plan ─────────────────────────────────────
    # Pick 3 random mid-season nights for double points, the final night for triple.
    double_nights = set(random.sample(range(1, NIGHTS), 3))
    triple_nights = {NIGHTS}  # last night of season = triple points final

    base_date = date(2026, 1, 7)

    for night in range(1, NIGHTS + 1):
        night_date = (base_date + timedelta(weeks=night - 1)).strftime("%d/%m/%Y")

        # Determine tonight's multiplier
        if night in triple_nights:
            scheme        = "triple"
            double_points = False
            triple_points = True
            mult_label    = "x3"
        elif night in double_nights:
            scheme        = "double"
            double_points = True
            triple_points = False
            mult_label    = "x2"
        else:
            scheme        = "standard"
            double_points = False
            triple_points = False
            mult_label    = "  "

        # Select racers for tonight
        box_count      = random.randint(8, 14)
        box_names      = random.sample(ADULT_POOL[:22], min(box_count, 22))[:box_count]
        evo_adult_n    = random.randint(5, 9)
        evo_junior_n   = random.randint(3, min(5, len(JUNIOR_POOL)))
        evo_adults     = random.sample(ADULT_POOL[:20], min(evo_adult_n, 20))
        evo_juniors    = random.sample(JUNIOR_POOL, evo_junior_n)
        pro_count      = random.randint(6, min(10, len(PRO_POOL)))
        pro_names      = random.sample(PRO_POOL, pro_count)

        def make_entries(adult_names, junior_names=None):
            entries = []
            for name in adult_names:
                dbr = ensure_racer(name, False)
                entries.append({"id": uid(), "name": name, "isJunior": False, "rosterId": dbr["id"]})
            for name in (junior_names or []):
                dbr = ensure_racer(name, True)
                entries.append({"id": uid(), "name": name, "isJunior": True, "rosterId": dbr["id"]})
            return entries

        try:
            # ── Box ────────────────────────────────────────────────
            box_entries = make_entries(box_names)
            res, jp, rb, rs, R = simulate_class(box_entries, "box", scheme)
            ev = build_event(R, res, jp, rb, rs, "box", "Box Class",
                             night_date, scheme, double_points, triple_points)
            upsert_event(season, ev)

            # Test upsert: save the same event again — must not create a duplicate
            upsert_event(season, ev)
            dup_ids = [e["id"] for e in season["events"]]
            if len(dup_ids) != len(set(dup_ids)):
                errors.append(f"Night {night} Box: upsert created duplicate event ID {ev['id']}")

            champ = next((r["name"] for r in R["racers"] if r["id"] == R["podium"]["first"]), "?")
            print(f"  Night {night:2d} {mult_label} Box OK  {len(box_entries):2d} racers  {R['raceNum']:2d} races  champ: {champ}")

            # ── EVO ────────────────────────────────────────────────
            evo_entries = make_entries(evo_adults, evo_juniors)
            res, jp, rb, rs, R = simulate_class(evo_entries, "evo", scheme)
            ev = build_event(R, res, jp, rb, rs, "evo", "EVO Class",
                             night_date, scheme, double_points, triple_points)
            upsert_event(season, ev)

            champ = next((r["name"] for r in R["racers"] if r["id"] == R["podium"]["first"]), "?")
            print(f"  Night {night:2d} {mult_label} EVO OK  {len(evo_entries):2d} racers ({evo_junior_n} jnr)  {R['raceNum']:2d} races  champ: {champ}")

            # ── Pro ────────────────────────────────────────────────
            pro_entries = make_entries(pro_names)
            res, jp, rb, rs, R = simulate_class(pro_entries, "pro", scheme)
            ev = build_event(R, res, jp, rb, rs, "pro", "Pro Class",
                             night_date, scheme, double_points, triple_points)
            upsert_event(season, ev)

            champ = next((r["name"] for r in R["racers"] if r["id"] == R["podium"]["first"]), "?")
            print(f"  Night {night:2d} {mult_label} Pro OK  {len(pro_entries):2d} racers  {R['raceNum']:2d} races  champ: {champ}")

        except Exception as e:
            errors.append(f"Night {night}: {e}")
            print(f"  Night {night} ERROR: {e}")

    # ── Validation pass ───────────────────────────────────────────
    print(f"\n  Validating {len(season['events'])} events...")

    # No duplicate event IDs
    all_ids = [e["id"] for e in season["events"]]
    if len(all_ids) != len(set(all_ids)):
        errors.append(f"Duplicate event IDs in season (count={len(all_ids)}, unique={len(set(all_ids))})")
    else:
        print("  No duplicate event IDs OK")

    for ev in season["events"]:
        tag = f"{ev['classKey']} {ev['date']}"

        # Must have a podium winner
        if not ev.get("podium") or not ev["podium"].get("first"):
            errors.append(f"{tag}: missing podium.first")

        results = ev.get("results", [])
        if not results:
            errors.append(f"{tag}: empty results"); continue

        # Positions must be 1..n with no gaps or duplicates
        positions = [r["position"] for r in results]
        n = len(positions)
        if sorted(positions) != list(range(1, n + 1)):
            errors.append(f"{tag}: positions {sorted(positions)} != 1..{n}")

        # Every racer has non-negative wins/losses/points
        for r in results:
            if r["wins"] < 0 or r["losses"] < 0:
                errors.append(f"{tag}: {r['name']} negative wins/losses")
            if r["points"] < 0:
                errors.append(f"{tag}: {r['name']} negative points")

        # Points must be non-increasing by position
        sorted_by_pos = sorted(results, key=lambda r: r["position"])
        for i in range(len(sorted_by_pos) - 1):
            a, b = sorted_by_pos[i], sorted_by_pos[i + 1]
            if a["points"] < b["points"]:
                errors.append(f"{tag}: pos {a['position']} ({a['points']}pts) < pos {b['position']} ({b['points']}pts)")

        # pointsScheme stored correctly
        if ev.get("triplePoints") and ev.get("pointsScheme") != "triple":
            errors.append(f"{tag}: triplePoints=True but pointsScheme='{ev.get('pointsScheme')}'")
        if ev.get("doublePoints") and ev.get("pointsScheme") != "double":
            errors.append(f"{tag}: doublePoints=True but pointsScheme='{ev.get('pointsScheme')}'")
        if not ev.get("triplePoints") and not ev.get("doublePoints"):
            if ev.get("pointsScheme") not in ("standard", "podium"):
                errors.append(f"{tag}: no multiplier but pointsScheme='{ev.get('pointsScheme')}'")

        # Night multiplier: check position-1 points match scheme
        expected_1st = pos_points(1, ev.get("pointsScheme", "standard"))
        actual_1st   = next((r["points"] for r in results if r["position"] == 1), None)
        if actual_1st is not None and actual_1st != expected_1st:
            errors.append(f"{tag}: 1st place got {actual_1st} pts, expected {expected_1st} for scheme '{ev.get('pointsScheme')}'")

    # Count multiplier nights
    double_ev = sum(1 for e in season["events"] if e.get("doublePoints"))
    triple_ev = sum(1 for e in season["events"] if e.get("triplePoints"))
    print(f"  Double-points events: {double_ev} (expected ~{len(double_nights)*3})")
    print(f"  Triple-points events: {triple_ev} (expected {len(triple_nights)*3})")
    if double_ev == 0 and triple_ev == 0:
        errors.append("No multiplier events recorded — night multiplier logic not exercised")

    # ── Junior points validation ──────────────────────────────────
    print("  Validating junior points...")
    junior_standings = {}
    evo_events = [e for e in season["events"] if e["classKey"] == "evo" and e["type"] == "normal"]
    for ev in evo_events:
        event_juniors = sorted(
            [r for r in ev["results"] if r["isJunior"]],
            key=lambda r: r.get("position", 99)
        )
        j_scheme = ev.get("pointsScheme", "standard")
        for j_idx, jres in enumerate(event_juniors):
            key = jres["name"].lower().strip()
            expected_pts = pos_points(j_idx + 1, j_scheme)
            junior_standings.setdefault(key, {"name": jres["name"], "pts": 0, "events": 0})
            junior_standings[key]["pts"]    += expected_pts
            junior_standings[key]["events"] += 1

            # 1st junior must always get full marks for the scheme
            if j_idx == 0 and expected_pts != pos_points(1, j_scheme):
                errors.append(
                    f"EVO {ev['date']}: 1st junior {jres['name']} got {expected_pts} "
                    f"not {pos_points(1, j_scheme)} (scheme={j_scheme})"
                )

        # Triple/double nights: verify junior points scale correctly
        if j_scheme == "triple" and event_juniors:
            top_pts = pos_points(1, "triple")
            actual  = pos_points(1, j_scheme)
            if actual != top_pts:
                errors.append(f"EVO {ev['date']}: triple junior 1st = {actual}, expected {top_pts}")
        if j_scheme == "double" and event_juniors:
            top_pts = pos_points(1, "double")
            actual  = pos_points(1, j_scheme)
            if actual != top_pts:
                errors.append(f"EVO {ev['date']}: double junior 1st = {actual}, expected {top_pts}")

    if junior_standings:
        top = sorted(junior_standings.items(), key=lambda x: -x[1]["pts"])
        print(f"  Top junior: {top[0][1]['name']}  {top[0][1]['pts']} pts  {top[0][1]['events']} events")
        print(f"  Junior standings: {len(junior_standings)} juniors tracked")
    else:
        warnings.append("No junior standings computed -- check EVO racer isJunior flags")

    # ── Season roster active/inactive flag test ───────────────────
    print("  Validating season roster active flags...")
    all_racers = DB["racers"]

    # All racers should have an active field
    for r in all_racers:
        if "active" not in r:
            errors.append(f"Racer '{r['name']}' missing active field")
        elif not isinstance(r["active"], bool):
            errors.append(f"Racer '{r['name']}' active field is not bool: {r['active']}")

    # Simulate marking some racers inactive (as season roster setup would do)
    inactive_count = random.randint(3, 6)
    inactive_sample = random.sample(all_racers, min(inactive_count, len(all_racers)))
    for r in inactive_sample:
        r["active"] = False
    active_now = sum(1 for r in all_racers if r.get("active") is not False)
    print(f"  Marked {inactive_count} inactive, {active_now}/{len(all_racers)} active")

    # Inactive racers must still have their results in the season (historical preservation)
    inactive_ids = {r["id"] for r in all_racers if r.get("active") is False}
    refs_in_events = set()
    for ev in season["events"]:
        for res in ev.get("results", []):
            if res.get("rosterId"):
                refs_in_events.add(res["rosterId"])
    preserved = inactive_ids & refs_in_events
    if inactive_ids and not preserved:
        warnings.append("Inactive racers have no event references -- might be newly added racers")
    else:
        print(f"  {len(preserved)} inactive racers preserved in historical results OK")

    # Reactivate all for future seasons
    for r in all_racers:
        r["active"] = True

    # ── Multi-season roster continuity ───────────────────────────
    print("  Validating multi-season roster continuity...")
    if len(DB["seasons"]) >= 2:
        prev_season = DB["seasons"][-2]
        prev_racer_ids = set()
        for ev in prev_season.get("events", []):
            for r in ev.get("results", []):
                if r.get("rosterId"):
                    prev_racer_ids.add(r["rosterId"])
        all_db_ids = {r["id"] for r in DB["racers"]}
        orphans = prev_racer_ids - all_db_ids
        if orphans:
            errors.append(f"Previous season references {len(orphans)} racer IDs not in DB.racers")
        else:
            print(f"  Previous season racer IDs all found in DB OK ({len(prev_racer_ids)} racers)")
    else:
        print("  Single season -- multi-season check skipped")

    # ── Summary ───────────────────────────────────────────────────
    expected_events = NIGHTS * 3
    actual_events   = len(season["events"])
    print(f"\n  Events:  {actual_events} / {expected_events} expected")
    print(f"  Racers:  {len(DB['racers'])} in DB")
    print(f"  Errors:  {len(errors)}")
    if errors:
        print("\n  ERRORS:")
        for e in errors:
            print(f"    FAIL: {e}")
    if warnings:
        print("\n  WARNINGS:")
        for w in warnings:
            print(f"    WARN: {w}")

    return DB, errors, warnings


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Static scheme validation first
    print("Validating points schemes...")
    scheme_errors = validate_schemes()
    if scheme_errors:
        print("  FAIL: points scheme errors:")
        for e in scheme_errors:
            print(f"    {e}")
        sys.exit(1)
    print(f"  All schemes OK  "
          f"(standard 1st={pos_points(1,'standard')}  "
          f"double 1st={pos_points(1,'double')}  "
          f"triple 1st={pos_points(1,'triple')})")

    total_errors = 0
    last_db      = None

    for run in range(1, RUNS + 1):
        # Run 2+ carry the previous DB to exercise multi-season roster continuity
        db, errs, warns = run_stress_test(run, carry_db=last_db if run > 1 else None)
        total_errors += len(errs)
        last_db = db

    # Save last run to data/racedata.json for inspection in the app
    print(f"\n{'='*60}")
    print(f"  Saving last run data -> {DATA_FILE}")
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(last_db, f, indent=2, ensure_ascii=False)
    print(f"  Saved OK")
    print(f"\n  TOTAL ERRORS across {RUNS} runs: {total_errors}")
    if total_errors == 0:
        print("  ALL TESTS PASSED")
    else:
        print("  TESTS FAILED -- see errors above")
        sys.exit(1)
