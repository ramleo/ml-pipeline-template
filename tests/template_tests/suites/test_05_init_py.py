"""
test_05_init_py.py — Run init.py (Python CLI mode) end-to-end.

What we test:
  5a. init.py option 2 exits successfully
  5b. Project directory created with correct name + timestamp
  5c. .venv/ exists with Python binary
  5d. .ml_config.json has all required keys and correct values
  5e. All template files copied into project
  5f. Staging approach used: copy → venv → pip → atomic move (output check)
  5g. Dataset CSV is copied when path is provided
  5h. requirements.txt present in created project

NOTE: This test runs pip install. Use --fast to skip.
"""
import os, subprocess, json, time, sys, stat
from pathlib import Path
from typing import List, Optional
from .base import (
    TEMPLATE_DIR, FIXTURES_DIR,
    REQUIRED_PROJECT_FILES, ML_CONFIG_REQUIRED_KEYS,
    TestResult, run_test, passresult, failresult, skip,
    copy_template_to_temp, make_fake_claude_bin, find_created_project,
)

SUITE_NAME = "Suite 05 — init.py (Python CLI Mode)"

PROJECT_NAME = "test-py-project"

# init.py prompts (mode_select shows 1/2/3):
# 2  = Python CLI mode (stays in init.py, does full setup)
# PROJECT_NAME = project name
# (empty) = no CSV
# 1  = deploy: ask_later
# (empty) = github username (skip or accept auto-detected)
# (empty) = repo name (accept default if prompted)
# 1  = visibility (public if prompted)
# (empty) x3 = padding
INIT_PY_INPUTS_NO_CSV = f"2\n{PROJECT_NAME}\n\n1\n\n\n1\n\n\n"

# ── Shared state (project created once) ───────────────────────────────
_shared_project: Optional[Path] = None
_shared_result:  Optional[subprocess.CompletedProcess] = None
_setup_error:    Optional[str] = None


def _ensure_project_created():
    global _shared_project, _shared_result, _setup_error
    if _shared_result is not None:
        return

    tmpl_copy = copy_template_to_temp()
    bin_dir   = make_fake_claude_bin(tmpl_copy.parent)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    before = time.time()
    try:
        _shared_result = subprocess.run(
            [sys.executable, str(tmpl_copy / "init.py")],
            input=INIT_PY_INPUTS_NO_CSV,
            env=env,
            capture_output=True, text=True,
            timeout=360,
            cwd=str(tmpl_copy),
        )
    except subprocess.TimeoutExpired:
        _setup_error = "init.py timed out after 360s"
        _shared_result = subprocess.CompletedProcess(args=[], returncode=-1, stdout="", stderr="TIMEOUT")
        return

    _shared_project = find_created_project(tmpl_copy.parent, PROJECT_NAME, before)
    if _shared_project is None:
        _setup_error = (
            f"Project dir '{PROJECT_NAME}_*' not found in {tmpl_copy.parent}\n"
            f"stdout: {_shared_result.stdout[-500:]}\n"
            f"stderr: {_shared_result.stderr[-300:]}"
        )


def _test_init_py_exits_ok() -> TestResult:
    _ensure_project_created()
    if _setup_error and "not found" not in _setup_error:
        return failresult("init.py: exits with code 0", _setup_error)
    if _shared_result is None:
        return failresult("init.py: exits with code 0", "setup did not run")
    rc = _shared_result.returncode
    if rc != 0:
        return failresult(
            "init.py: exits with code 0",
            f"Exit code {rc}",
            details=(
                f"STDOUT (last 500):\n{_shared_result.stdout[-500:]}\n"
                f"STDERR (last 300):\n{_shared_result.stderr[-300:]}"
            ),
        )
    return passresult("init.py: exits with code 0")


def _test_project_dir_created() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: project directory created", _setup_error or "Unknown")
    return passresult("init.py: project directory created", str(_shared_project.name))


def _test_venv_exists() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: .venv/ exists in project", _setup_error or "Project not created")
    venv = _shared_project / ".venv"
    if not venv.exists():
        return failresult("init.py: .venv/ exists in project", ".venv/ not found")
    python = venv / "bin" / "python"
    if not python.exists():
        return failresult("init.py: .venv/ exists in project", ".venv/ found but .venv/bin/python missing")
    return passresult("init.py: .venv/ exists in project")


def _test_ml_config_valid() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: .ml_config.json valid", _setup_error or "Project not created")

    cfg_path = _shared_project / ".ml_config.json"
    if not cfg_path.exists():
        return failresult("init.py: .ml_config.json valid", ".ml_config.json not found")
    try:
        cfg = json.loads(cfg_path.read_text())
    except json.JSONDecodeError as e:
        return failresult("init.py: .ml_config.json valid", f"Invalid JSON: {e}")

    missing = [k for k in ML_CONFIG_REQUIRED_KEYS if k not in cfg]
    if missing:
        return failresult("init.py: .ml_config.json valid", f"Missing keys: {missing}")

    checks = [
        ("project_name correct", cfg["project_name"] == PROJECT_NAME),
        ("venv_path is .venv", cfg["venv_path"] == ".venv"),
        ("template_version present", bool(cfg.get("template_version"))),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("init.py: .ml_config.json valid", f"Value checks failed: {failed}")
    return passresult("init.py: .ml_config.json valid", f"{len(ML_CONFIG_REQUIRED_KEYS)} keys verified")


def _test_template_files_copied() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: template files copied", _setup_error or "Project not created")
    missing = [f for f in REQUIRED_PROJECT_FILES if not (_shared_project / f).exists()]
    if missing:
        return failresult(
            "init.py: template files copied",
            f"{len(missing)} file(s) missing",
            details="\n".join(f"  MISSING: {f}" for f in missing),
        )
    return passresult("init.py: template files copied", f"{len(REQUIRED_PROJECT_FILES)} files present")


def _test_staging_approach_used() -> TestResult:
    """
    Staging approach: copy_template → create_venv → install_deps (all in /tmp),
    then one atomic move_to_final(). Verify console output confirms this order —
    meaning VS Code sees the project appear ONCE, complete, not incrementally.
    """
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: staging approach (atomic project creation)", _setup_error or "Project not created")

    stdout = _shared_result.stdout if _shared_result else ""

    # Check all staging-phase messages appear in output
    staging_msgs = [
        "Preparing template files",   # copy_template to staging
        "Creating Python virtual",    # create_venv in staging
        "Installing dependencies",    # install_deps in staging
        "Creating project at:",       # move_to_final → VS Code sees project once
    ]
    missing_msgs = [s for s in staging_msgs if s not in stdout]
    if missing_msgs:
        return failresult(
            "init.py: staging approach (atomic project creation)",
            f"Missing expected output messages: {missing_msgs}",
            details=f"stdout (last 600):\n{stdout[-600:]}",
        )

    # Verify messages appear in correct order
    prep_pos = stdout.find("Preparing template files")
    venv_pos = stdout.find("Creating Python virtual")
    pip_pos  = stdout.find("Installing dependencies")
    mv_pos   = stdout.find("Creating project at:")

    if not (prep_pos < venv_pos < pip_pos < mv_pos):
        return failresult(
            "init.py: staging approach (atomic project creation)",
            f"Staging steps out of order (prep={prep_pos}, venv={venv_pos}, pip={pip_pos}, mv={mv_pos})"
        )

    return passresult("init.py: staging approach (atomic project creation)",
                      "copy → venv → pip → atomic move order confirmed in output")


def _test_csv_copied_when_provided() -> TestResult:
    sample_csv = FIXTURES_DIR / "titanic_sample.csv"
    if not sample_csv.exists():
        return skip("init.py: CSV copied when path provided", "fixtures/titanic_sample.csv not found")

    tmpl_copy = copy_template_to_temp()
    bin_dir   = make_fake_claude_bin(tmpl_copy.parent)
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"

    inputs = f"2\ntest-py-csv\n{sample_csv}\n1\n\n\n1\n\n\n"
    before = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(tmpl_copy / "init.py")],
            input=inputs, env=env,
            capture_output=True, text=True,
            timeout=360, cwd=str(tmpl_copy),
        )
    except subprocess.TimeoutExpired:
        return failresult("init.py: CSV copied when path provided", "Timed out")

    project = find_created_project(tmpl_copy.parent, "test-py-csv", before)
    if project is None:
        return failresult("init.py: CSV copied when path provided",
                          f"Project not created\nstdout: {result.stdout[-300:]}")

    csv_in_project = project / "data" / "titanic_sample.csv"
    if not csv_in_project.exists():
        return failresult("init.py: CSV copied when path provided",
                          f"CSV not found at {csv_in_project}")
    return passresult("init.py: CSV copied when path provided",
                      f"CSV at data/{csv_in_project.name}")


def _test_requirements_txt_in_project() -> TestResult:
    _ensure_project_created()
    if _shared_project is None:
        return failresult("init.py: requirements.txt in project", _setup_error or "Project not created")
    req = _shared_project / "requirements.txt"
    if not req.exists():
        return failresult("init.py: requirements.txt in project", "requirements.txt not found")
    content = req.read_text()
    if "scikit-learn" not in content and "sklearn" not in content:
        return failresult("init.py: requirements.txt in project",
                          "requirements.txt found but scikit-learn not listed")
    return passresult("init.py: requirements.txt in project")


def run_suite(fast: bool = False) -> List[TestResult]:
    if fast:
        return [skip("init.py Python CLI (all tests)", "Skipped in --fast mode (requires pip install ~2 min)")]
    tests = [
        ("init.py: exits with code 0",            _test_init_py_exits_ok),
        ("init.py: project dir created",           _test_project_dir_created),
        ("init.py: .venv/ exists",                 _test_venv_exists),
        ("init.py: .ml_config.json valid",         _test_ml_config_valid),
        ("init.py: template files copied",         _test_template_files_copied),
        ("init.py: staging approach used",          _test_staging_approach_used),
        ("init.py: CSV copied when provided",      _test_csv_copied_when_provided),
        ("init.py: requirements.txt in project",   _test_requirements_txt_in_project),
    ]
    return [run_test(name, func) for name, func in tests]


if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
