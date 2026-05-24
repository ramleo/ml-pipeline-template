#!/usr/bin/env python3
"""
test_runner.py — ML Pipeline Template — Automated Test Runner

Usage:
  python3 test_runner.py            # run all suites (slow suites include pip install)
  python3 test_runner.py --fast     # skip suites that require pip install (~2 min each)
  python3 test_runner.py --suite 01 # run only suite 01 (by number prefix)
  python3 test_runner.py --suite bootstrap   # run by keyword

Suites:
  01  Prerequisites & Template Integrity   (fast, ~3s)
  02  Template File Content Validation     (fast, ~2s)
  03  bootstrap.py Behaviour               (medium, ~15s)
  04  start.sh Shell Mode                  (slow, ~3-4 min with pip install)
  05  init.py Python CLI Mode              (slow, ~3-4 min with pip install)
  06  Project Structure Deep Validation    (medium, ~15s)
"""

import sys, os, time, argparse, importlib
from pathlib import Path
from typing import List

# Make suites importable
RUNNER_DIR = Path(__file__).parent
sys.path.insert(0, str(RUNNER_DIR))

from suites.base import TestResult, G, R, Y, C, B, X, RESULTS_DIR


# ── Suite registry ─────────────────────────────────────────────────────
SUITES = [
    ("01", "test_01_prerequisites",    "Prerequisites & Template Integrity",   False),
    ("02", "test_02_template_files",   "Template File Content Validation",      False),
    ("03", "test_03_bootstrap",        "bootstrap.py Behaviour",                False),
    ("04", "test_04_start_sh",         "start.sh Shell Mode",                   True),   # slow
    ("05", "test_05_init_py",          "init.py Python CLI Mode",               True),   # slow
    ("06", "test_06_project_structure","Project Structure Deep Validation",      False),
]


# ── Reporting ──────────────────────────────────────────────────────────
def print_suite_header(suite_name: str):
    print(f"\n{C}{B}{'─' * 60}{X}")
    print(f"{C}{B}  {suite_name}{X}")
    print(f"{C}{B}{'─' * 60}{X}")


def print_summary(all_results: List[TestResult], total_time: float, log_path: Path):
    passed  = sum(1 for r in all_results if r.passed)
    failed  = sum(1 for r in all_results if not r.passed and not r.skipped)
    skipped = sum(1 for r in all_results if r.skipped)
    total   = len(all_results)

    print(f"\n{B}{'═' * 60}{X}")
    print(f"{B}  TEST SUMMARY{X}")
    print(f"{B}{'═' * 60}{X}")
    print(f"  {G}PASSED{X}  : {passed:3d}")
    if failed:
        print(f"  {R}FAILED{X}  : {failed:3d}")
    if skipped:
        print(f"  {Y}SKIPPED{X} : {skipped:3d}")
    print(f"  TOTAL   : {total:3d}")
    print(f"  Time    : {total_time:.1f}s")
    print(f"{B}{'─' * 60}{X}")

    if failed == 0:
        print(f"\n  {G}{B}✅  All tests passed!{X}")
    else:
        print(f"\n  {R}{B}❌  {failed} test(s) FAILED — see details above{X}")
        print(f"\n  {R}Failed tests:{X}")
        for r in all_results:
            if not r.passed and not r.skipped:
                print(f"    • {r.name}")
                if r.message:
                    print(f"      → {r.message}")

    print(f"\n  Results log: {log_path}")
    print(f"{B}{'═' * 60}{X}\n")


def write_log(all_results: List[TestResult], total_time: float, log_path: Path):
    lines = [
        "ML Pipeline Template — Test Results",
        f"Run at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total time: {total_time:.1f}s",
        "",
    ]
    for r in all_results:
        status = r.status
        line = f"[{status}] {r.name}"
        if r.duration >= 0.5:
            line += f"  ({r.duration:.1f}s)"
        lines.append(line)
        if not r.passed and not r.skipped and r.message:
            lines.append(f"       → {r.message}")
        if not r.passed and not r.skipped and r.details:
            for dl in r.details.strip().split("\n"):
                lines.append(f"         {dl}")

    passed  = sum(1 for r in all_results if r.passed)
    failed  = sum(1 for r in all_results if not r.passed and not r.skipped)
    skipped = sum(1 for r in all_results if r.skipped)

    lines += [
        "",
        f"PASSED: {passed}  FAILED: {failed}  SKIPPED: {skipped}  TOTAL: {len(all_results)}",
    ]

    RESULTS_DIR.mkdir(exist_ok=True)
    log_path.write_text("\n".join(lines))


# ── Suite loader ───────────────────────────────────────────────────────
def load_suite(module_name: str):
    return importlib.import_module(f"suites.{module_name}")


def run_suite_module(module, fast: bool) -> List[TestResult]:
    """Call run_suite() on a module, passing fast= if supported."""
    import inspect
    sig = inspect.signature(module.run_suite)
    if "fast" in sig.parameters:
        return module.run_suite(fast=fast)
    return module.run_suite()


# ── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ML Pipeline Template Test Runner")
    parser.add_argument("--fast", action="store_true",
                        help="Skip slow suites (04, 05) that run pip install")
    parser.add_argument("--suite", metavar="KEYWORD",
                        help="Run only suites matching this keyword (e.g. '01', 'bootstrap')")
    args = parser.parse_args()

    # ── Banner ──────────────────────────────────────────────────────
    print(f"""
{C}{B}╔══════════════════════════════════════════════════════════════╗
║      🧪  ML Pipeline Template — Automated Test Suite         ║
║      Tests every option described in docs/how_to_run.md      ║
╚══════════════════════════════════════════════════════════════╝{X}""")

    if args.fast:
        print(f"  {Y}Mode: --fast  (suites 04 and 05 skipped){X}")
    if args.suite:
        print(f"  {Y}Filter: --suite '{args.suite}'{X}")

    # ── Select suites ────────────────────────────────────────────────
    selected = SUITES
    if args.suite:
        kw = args.suite.lower()
        selected = [(n, m, label, slow) for n, m, label, slow in SUITES
                    if kw in n or kw in m.lower() or kw in label.lower()]
        if not selected:
            print(f"\n{R}No suites match '{args.suite}'.{X}")
            print("Available suites:")
            for n, m, label, _ in SUITES:
                print(f"  {n}: {label}")
            sys.exit(1)

    # ── Run suites ───────────────────────────────────────────────────
    all_results: List[TestResult] = []
    grand_start = time.time()
    log_path = RESULTS_DIR / f"test_run_{time.strftime('%Y%m%d_%H%M%S')}.txt"

    for suite_num, module_name, suite_label, is_slow in selected:
        if args.fast and is_slow:
            print_suite_header(f"Suite {suite_num} — {suite_label}  {Y}[SKIPPED — use without --fast]{X}")
            from suites.base import skip
            all_results.append(skip(suite_label, "--fast mode"))
            continue

        print_suite_header(f"Suite {suite_num} — {suite_label}")
        suite_start = time.time()

        try:
            module  = load_suite(module_name)
            results = run_suite_module(module, fast=args.fast)
        except Exception as e:
            from suites.base import failresult
            results = [failresult(suite_label, f"Suite failed to load/run: {e}")]

        for r in results:
            print(r)
            all_results.append(r)

        suite_time = time.time() - suite_start
        s_pass  = sum(1 for r in results if r.passed)
        s_fail  = sum(1 for r in results if not r.passed and not r.skipped)
        s_skip  = sum(1 for r in results if r.skipped)
        colour  = G if s_fail == 0 else R
        print(f"\n  {colour}Suite {suite_num}: {s_pass} passed, {s_fail} failed, {s_skip} skipped  ({suite_time:.1f}s){X}")

    # ── Summary ──────────────────────────────────────────────────────
    total_time = time.time() - grand_start
    print_summary(all_results, total_time, log_path)
    write_log(all_results, total_time, log_path)

    failed_count = sum(1 for r in all_results if not r.passed and not r.skipped)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
