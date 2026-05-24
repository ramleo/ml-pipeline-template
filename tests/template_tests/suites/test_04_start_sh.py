"""
test_04_start_sh.py — Run start.sh (option 1: Shell mode) end-to-end.

What we test:
  4a. start.sh option 1 exits successfully
  4b. Project directory created in parent of template copy
  4c. .venv/ exists in the created project
  4d. .ml_config.json exists with all required keys
  4e. All template files copied into project
  4f. .venv was created BEFORE other project folders (timestamp check)
  4g. Dataset CSV is copied when path is provided
  4h. requirements.txt present in created project

NOTE: This test runs pip install and takes ~2 minutes on first run.
      Use --fast flag to skip this suite.
"""
import os, subprocess, shutil, tempfile, json, time, stat
from pathlib import Path
from typing import List, Optional
from .base import (
    TEMPLATE_DIR, FIXTURES_DIR,
    REQUIRED_PROJECT_FILES, REQUIRED_PROJECT_DIRS, ML_CONFIG_REQUIRED_KEYS,
    TestResult, run_test, passresult, failresult, skip,
    copy_template_to_temp, make_fake_claude_bin, find_created_project,
)

SUITE_NAME = "Suite 04 — start.sh (Shell Mode, Option 1)"

PROJECT_NAME = "test-sh-project"

# Input sequence for start.sh option 1 (shell mode):
# 1  = shell mode (not Python, not Claude)
# PROJECT_NAME = project name
# (empty) = no CSV
# 1  = deploy: ask_later
# (empty) = github username (skip or accept auto-detected)
# (empty) = repo name (accept default, if prompted)
# 1  = visibility (public, if prompted)
# (empty) x3 = padding for any extra prompts
START_SH_INPUTS_NO_CSV = f"1\n{PROJECT_NAME}\n\n1\n\n\n1\n\n\n"

# With CSV
START_SH_INPUTS_WITH_CSV = ""  # built dynamically with CSV path


def _create_temp_template_and_env():
    """
    Copy template to /tmp, set up fake claude binary.
    Returns (tmpl_copy_path, env_dict, fake_bin_dir_path)
    """
    tmpl_copy = copy_template_to_temp()
    bin_dir = make_fake_claude_bin(tmpl_copy.parent)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    return tmpl_copy, env, bin_dir


def _run_start_sh(tmpl_copy: Path, env: dict, inputs: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run start.sh from the template copy with piped inputs."""
    sh = tmpl_copy / "start.sh"
    # Ensure it's executable
    sh.chmod(sh.stat().st_mode | stat.S_IEXEC)
    return subprocess.run(
        ["bash", str(sh)],
        input=inputs,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(tmpl_copy),
    )


def _find_project(tmpl_copy: Path, before_time: float) -> Optional[Path]:
    """Look for the created project in the parent of the template copy."""
    parent = tmpl_copy.parent
    return find_created_project(parent, PROJECT_NAME, before_time)


# ── Individual tests share a single project creation ──────────────────
_shared_project: Optional[Path] = None
_shared_result: Optional[subprocess.CompletedProcess] = None
_setup_error: Optional[str] = None


def _ensure_project_created():
    global _shared_project, _shared_result, _setup_error
    if _shared_result is not None:
        return

    tmpl_copy, env, _ = _create_temp_template_and_env()
    before = time.time()
    try:
        _shared_result = _run_start_sh(tmpl_copy, env, START_SH_INPUTS_NO_CSV, timeout=360)
    except subprocess.TimeoutExpired:
        _setup_error = "start.sh timed out after 360s"
        _shared_result = subprocess.CompletedProcess(args=[], returncode=-1, stdout="", stderr="TIMEOUT")
        return

    _shared_project = _find_project(tmpl_copy, before)
    if _shared_project is None:
        _setup_error = (
            f"Project dir '{PROJECT_NAME}_*' not found in {tmpl_copy.parent}\n"
            f"stdout: {_shared_result.stdout[-500:]}\n"
            f"stderr: {_shared_result.stderr[-300:]}"
        )


def _test_start_sh_exits_ok() -> TestResult:
    _ensure_project_created()
    if _setup_error and "not found" not in _setup_error:
        return failresult("start.sh option 1: exits with code 0", _setup_error)
    if _shared_result is None:
        return failresult("start.sh option 1: exits with code 0", "setup did not run")
    rc = _shared_result.returncode
    if rc != 0:
        return failresult(
            "start.sh option 1: exits with code 0",
            f"Exit code {rc}",
            details=(
                f"STDOUT (last 500):\n{_shared_result.stdout[-500:]}\n"
                f"STDERR (last 300):\n{_shared_result.stderr[-300:]}"
            ),
        )
    return passresult("start.sh option 1: exits with code 0")


def _test_project_dir_created() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        err = _setup_error or "Unknown error"
        return failresult("start.sh: project directory created", err)
    return passresult("start.sh: project directory created", str(_shared_project.name))


def _test_venv_exists() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("start.sh: .venv/ exists in project", _setup_error or "Project not created")
    venv = _shared_project / ".venv"
    if not venv.exists():
        return failresult("start.sh: .venv/ exists in project", ".venv/ not found")
    # Check it has a python binary
    python = venv / "bin" / "python"
    if not python.exists():
        return failresult("start.sh: .venv/ exists in project", ".venv/ exists but .venv/bin/python missing")
    return passresult("start.sh: .venv/ exists in project")


def _test_ml_config_exists_and_valid() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("start.sh: .ml_config.json has all keys", _setup_error or "Project not created")
    cfg_path = _shared_project / ".ml_config.json"
    if not cfg_path.exists():
        return failresult("start.sh: .ml_config.json has all keys", ".ml_config.json not found")
    try:
        cfg = json.loads(cfg_path.read_text())
    except json.JSONDecodeError as e:
        return failresult("start.sh: .ml_config.json has all keys", f"Invalid JSON: {e}")

    missing = [k for k in ML_CONFIG_REQUIRED_KEYS if k not in cfg]
    if missing:
        return failresult("start.sh: .ml_config.json has all keys", f"Missing keys: {missing}")

    # Validate specific values
    checks = [
        ("project_name is correct", cfg["project_name"] == PROJECT_NAME),
        ("venv_path is .venv", cfg["venv_path"] == ".venv"),
        ("template_version present", bool(cfg.get("template_version"))),
        ("python_version present", bool(cfg.get("python_version"))),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("start.sh: .ml_config.json has all keys", f"Value checks failed: {failed}")

    return passresult("start.sh: .ml_config.json has all keys",
                      f"{len(ML_CONFIG_REQUIRED_KEYS)} keys present, values validated")


def _test_template_files_copied() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("start.sh: template files copied", _setup_error or "Project not created")

    missing = [f for f in REQUIRED_PROJECT_FILES if not (_shared_project / f).exists()]
    if missing:
        return failresult(
            "start.sh: template files copied",
            f"{len(missing)} file(s) missing",
            details="\n".join(f"  MISSING: {f}" for f in missing),
        )
    return passresult("start.sh: template files copied", f"{len(REQUIRED_PROJECT_FILES)} files present")


def _test_venv_created_before_folders() -> TestResult:
    """
    Critical fix: .venv should have been created (birthtime) BEFORE
    data/, src/, deploy/ etc. were copied by rsync.
    """
    _ensure_project_created()
    if _shared_project is None:
        return failresult("start.sh: .venv created before template folders", _setup_error or "Project not created")

    venv = _shared_project / ".venv"
    if not venv.exists():
        return failresult("start.sh: .venv created before template folders", ".venv not found")

    try:
        venv_btime = venv.stat().st_birthtime
    except AttributeError:
        return skip("start.sh: .venv created before template folders",
                    "st_birthtime not available on this OS (Linux); use macOS for this check")

    later_dirs = ["data", "src", "deploy", "docs", "tests"]
    order_violations = []
    for d in later_dirs:
        dirpath = _shared_project / d
        if not dirpath.exists():
            continue
        try:
            d_btime = dirpath.stat().st_birthtime
        except AttributeError:
            continue
        if venv_btime > d_btime + 0.5:   # allow 0.5s slack
            order_violations.append(
                f"{d}/ birthtime={d_btime:.3f} is earlier than .venv birthtime={venv_btime:.3f}"
            )

    if order_violations:
        return failresult(
            "start.sh: .venv created before template folders",
            f".venv was created AFTER some folders — venv-first fix is broken",
            details="\n".join(order_violations),
        )
    return passresult("start.sh: .venv created before template folders",
                      f".venv birthtime <= all {len(later_dirs)} template folders")


def _test_csv_copied_when_provided() -> TestResult:
    """Run start.sh again with a CSV path and verify it gets copied."""
    sample_csv = FIXTURES_DIR / "titanic_sample.csv"
    if not sample_csv.exists():
        return skip("start.sh: CSV copied when path provided", "fixtures/titanic_sample.csv not found")

    tmpl_copy, env, _ = _create_temp_template_and_env()
    inputs = f"1\ntest-sh-csv\n{sample_csv}\n1\n\n\n1\n\n\n"
    before = time.time()

    try:
        result = _run_start_sh(tmpl_copy, env, inputs, timeout=360)
    except subprocess.TimeoutExpired:
        return failresult("start.sh: CSV copied when path provided", "Timed out")

    project = find_created_project(tmpl_copy.parent, "test-sh-csv", before)
    if project is None:
        return failresult("start.sh: CSV copied when path provided",
                          f"Project not created\nstdout: {result.stdout[-300:]}")

    csv_in_project = project / "data" / "titanic_sample.csv"
    if not csv_in_project.exists():
        return failresult("start.sh: CSV copied when path provided",
                          f"CSV not found at {csv_in_project}")
    return passresult("start.sh: CSV copied when path provided",
                      f"CSV at data/{csv_in_project.name}")


def run_suite(fast: bool = False) -> List[TestResult]:
    if fast:
        return [skip("start.sh option 1 (all tests)", "Skipped in --fast mode (requires pip install ~2 min)")]
    tests = [
        ("start.sh option 1: exits code 0",         _test_start_sh_exits_ok),
        ("start.sh: project dir created",            _test_project_dir_created),
        ("start.sh: .venv/ exists",                  _test_venv_exists),
        ("start.sh: .ml_config.json valid",          _test_ml_config_exists_and_valid),
        ("start.sh: template files copied",          _test_template_files_copied),
        ("start.sh: .venv before template folders",  _test_venv_created_before_folders),
        ("start.sh: CSV copied when provided",       _test_csv_copied_when_provided),
    ]
    return [run_test(name, func) for name, func in tests]


if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
