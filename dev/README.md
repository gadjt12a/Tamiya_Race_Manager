# Developer material

Nothing in this folder is needed to *use* Race Manager. If you are here to
install or run the app, go back to the [main README](../README.md).

| File | What it is |
|---|---|
| [`BUILD.md`](BUILD.md) | Building all three packages from a clean checkout — Windows installer, Windows portable zip, Mac `.app`. Includes the smoke-test checklist and the gotchas worth knowing before you start. |
| [`DEPLOYMENT_PLAN.md`](DEPLOYMENT_PLAN.md) | The v10 packaging and release plan, phase by phase, and the honest status of each item. The place to look for what is still open. |
| [`TESTING_MANUAL.md`](TESTING_MANUAL.md) | The manual test matrix — the steps to run by hand and the results recorded against them. |
| [`PROJECT_MEMORY.md`](PROJECT_MEMORY.md) | Design decisions, the reasoning behind them, and known future items. Written so a new session can pick the project up cold. |
| [`stress-test.py`](stress-test.py) | Simulates 30 race nights and checks the bracket engine, points schemes and data integrity. Run it after touching any of those. |

Build scripts live with the platform they build: [`../windows/`](../windows/)
and [`../mac/`](../mac/).

```
python dev/stress-test.py        # from the repo root
```
