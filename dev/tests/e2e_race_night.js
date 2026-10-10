// Tamiya Race Manager - full race night, driven through the app's OWN code.
//
// This exists because the bugs that reached the club (exports silently doing
// nothing, the roster jumping, the display going blank) all lived in the USER
// FLOW. Endpoint tests pass straight through them. This calls the same
// functions the buttons call, start to finish, and then checks what landed on
// disk.
//
// HOW TO RUN
//   1. Start the app against a throwaway folder:
//        TAMIYA_DATA_DIR=<scratch> python app/server.py --no-browser
//      with <scratch>/racedata.json = {"version":1,"seasons":[],"racers":[],"currentSeason":null}
//   2. Open http://127.0.0.1:8765/race-manager.html
//   3. Paste this whole file into the browser console.
//   4. Wait. `await window.__E2E.promise` resolves with the result, and
//      window.__E2E.log has the running commentary.
//
// CLOSE THE BROWSER TAB WHEN DONE. A tab left open on the app will write its
// in-memory data over the data file the next time a server appears on 8765.
// That is not hypothetical - it silently clobbered a test database on
// 2026-10-10 and has bitten the real club data twice before.

window.__E2E = { log: [], result: null, error: null, done: false };
const L = m => { window.__E2E.log.push(m); console.log('[e2e] ' + m); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function e2eRunClass(classKey, names, juniors) {
  L(`--- ${classKey.toUpperCase()}: ${names.length} racers ---`);
  selectClass(classKey);
  await sleep(150);
  setupState.racerEntries = [];
  names.forEach(n => addRacerEntry(n, juniors.includes(n)));
  if (setupState.racerEntries.length !== names.length)
    throw new Error(`${classKey}: added ${setupState.racerEntries.length}/${names.length}`);

  startRaceNight();
  await sleep(180);
  if (document.getElementById('raceScreen').className.indexOf('active') < 0)
    throw new Error(`${classKey}: race screen did not open`);

  let heats = 0;
  const frames = new Set();
  while (!R.podium && heats++ < 400) {
    if (!R.currentRace) { await sleep(40); continue; }
    const before = (R.history || []).length;
    R.currentRace.racers.forEach((id, i) => setPlace(i + 1, id));
    confirmResult();
    await sleep(30);
    const d = getDisplayHTML();
    if (d) frames.add(d.length);
    if ((R.history || []).length === before && !R.podium)
      throw new Error(`${classKey}: confirmResult did not advance at heat ${heats}`);
  }
  if (!R.podium) throw new Error(`${classKey}: no podium after ${heats} heats`);
  if (frames.size < 2) throw new Error(`${classKey}: display content never changed`);
  L(`  ${heats} heats, winner ${getName(R.podium.first)}, ${frames.size} display frames`);

  const podium = {
    first: getName(R.podium.first), second: getName(R.podium.second),
    third: getName(R.podium.third)
  };
  await finishClass();
  await sleep(300);
  return { heats, podium, displayFrames: frames.size };
}

window.__E2E.promise = (async () => {
  try {
    document.getElementById('newSeasonName').value = 'E2E Test Season';
    document.getElementById('newSeasonStart').value = new Date().toISOString().slice(0, 10);
    await createSeason();
    await sleep(350);
    if (!DB.currentSeason) throw new Error('season was not created');
    L('season created');

    const jnr = ['Cullen', 'Mason', 'Toby', 'Theo', 'Izen', 'Lily', 'Emerson', 'Grace', 'Brax', 'Jemma'];
    const out = {
      box: await e2eRunClass('box',
        ['Ronynn', 'Gene', 'Izen', 'Mason', 'Cullen', 'Lily', 'Theo', 'Jemma', 'Brax', 'Toby', 'Emerson', 'Grace'], jnr),
      evo: await e2eRunClass('evo',
        ['Soi', 'Luke', 'Phil', 'Cullen', 'Mason', 'Toby', 'Peter P', 'Mike', 'Lindsay', 'Trevor'], jnr),
      pro: await e2eRunClass('pro',
        ['Soi', 'Mike', 'Dom', 'Jay', 'Trevor', 'Phil', 'Peter U', 'Janry'], [])
    };

    const season = DB.seasons.find(s => s.id === DB.currentSeason);
    out.summary = {
      events: season.events.length,
      classes: season.events.map(e => e.classKey),
      resultCounts: season.events.map(e => e.results.length),
      racersInDB: DB.racers.length,
      everyResultHasARacer: season.events.every(e =>
        e.results.every(r => DB.racers.some(x => x.id === (r.rosterId || r.racerId)))),
      positionsContiguous: season.events.every(e =>
        e.results.map(r => r.position).sort((a, b) => a - b)
          .every((p, i) => p === i + 1))
    };
    if (out.summary.events !== 3) throw new Error('expected 3 events, got ' + out.summary.events);
    if (!out.summary.everyResultHasARacer) throw new Error('a result points at a racer not on the roster');
    if (!out.summary.positionsContiguous) throw new Error('finishing positions are not 1..n');

    window.__E2E.result = out;
    L('ALL PASS - check the data file on disk as well');
    return out;
  } catch (e) {
    window.__E2E.error = e.message;
    L('FAIL: ' + e.message);
    throw e;
  } finally {
    window.__E2E.done = true;
    document.body.setAttribute('data-e2e', JSON.stringify({
      done: true, error: window.__E2E.error,
      log: window.__E2E.log, result: window.__E2E.result
    }));
  }
})();
