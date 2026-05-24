# ML Pipeline Template — Automated Test Suite

Tests every option and flow described in `docs/how_to_run.md`, catching bugs before users encounter them.

---

## Quick Start

```bash
cd tests/template_tests
chmod +x run_tests.sh

# Fast checks only (no pip install, ~30 seconds)
./run_tests.sh --fast

# Full suite (includes pip install, ~10 minutes)
./run_tests.sh
```

---

## What Is Tested

| Suite | Name | Speed | What it checks |
|---|---|---|---|
| 01 | Prerequisites & Template Integrity | ~3s | Python version, start.sh executable, all template files exist, venv-before-rsync code order |
| 02 | Template File Content Validation | ~2s | CLAUDE.md pipeline steps, sub-agent routing, deploy/docs/tests CLAUDE.md specs |
| 03 | bootstrap.py Behaviour | ~15s | Creates correct folder structure, custom names, error on duplicate |
| 04 | start.sh Shell Mode | ~3–4 min | Runs start.sh option 1 with piped inputs, verifies .venv created before template folders |
| 05 | init.py Python CLI Mode | ~3–4 min | Runs init.py option 2 with piped inputs, same structure checks |
| 06 | Project Structure Deep Validation | ~15s | All files/dirs in bootstrap output, settings.local.json clean, src/CLAUDE.md content |

---

## Options

```bash
./run_tests.sh                      # all suites
./run_tests.sh --fast               # suites 01–03 + 06 only (no pip install)
./run_tests.sh --suite 01           # run suite 01 only
./run_tests.sh --suite bootstrap    # run suite 03 (keyword match)
./run_tests.sh --suite start        # run suite 04
./run_tests.sh --suite init         # run suite 05
```

---

## What CANNOT Be Automated

| Scenario | Reason | How to test manually |
|---|---|---|
| Claude Code mode (`./start.sh` option 3) | Requires interactive Claude session | Run `./start.sh`, choose 3, provide Titanic CSV |
| Full ML pipeline (Steps 2–14) | Requires Claude Code running | Open project in Claude Code, say "Y" to proceed |
| Docker alternative | Requires Docker daemon | `docker build -t ml-pipeline-template -f Dockerfile.bootstrap .` |

---

## Test Output

Results are saved to `results/test_run_TIMESTAMP.txt` after each run.

---

## How It Works

1. **Suites 01–02**: Read-only static checks — parse file contents, check permissions
2. **Suite 03**: Runs `python3 bootstrap.py` in a temp directory (`/tmp/ml_bs_test_*/`)
3. **Suites 04–05**: Copy template to temp dir, run with piped inputs, intercept `claude .` with a fake binary
4. **Suite 06**: Runs bootstrap.py once and validates the output directory in depth

All test-created files go to `/tmp/` and are auto-cleaned by Python's `tempfile.TemporaryDirectory`.

---

## Files

```
tests/template_tests/
├── run_tests.sh           ← entry point (just run this)
├── README.md              ← this file
├── test_runner.py         ← orchestrator, reporting, CLI args
├── suites/
│   ├── base.py            ← shared helpers, TestResult class
│   ├── test_01_prerequisites.py
│   ├── test_02_template_files.py
│   ├── test_03_bootstrap.py
│   ├── test_04_start_sh.py
│   ├── test_05_init_py.py
│   └── test_06_project_structure.py
├── fixtures/
│   └── titanic_sample.csv ← 25-row Titanic dataset for CSV-copy tests
└── results/
    └── (test run logs)
```
