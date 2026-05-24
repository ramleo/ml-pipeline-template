"""
test_06_project_structure.py — Deep validation of a created project directory.

This suite uses bootstrap.py output (no pip install needed) to validate
the project layout without the full 2-minute setup time.

Tests:
  6a. All top-level files present
  6b. All required subdirectories present
  6c. .claude/settings.local.json valid in created project
  6d. CLAUDE.md content correct in project (not stale)
  6e. src/CLAUDE.md content correct in project
  6f. start.sh is executable in project
  6g. requirements.txt has all ML packages
  6h. README.md is non-empty
  6i. .gitkeep files present in empty dirs
"""
import json
from pathlib import Path
from typing import List
import tempfile, subprocess
from .base import (
    TEMPLATE_DIR, REQUIRED_PROJECT_DIRS, REQUIRED_PROJECT_FILES,
    TestResult, run_test, passresult, failresult, skip,
)

SUITE_NAME = "Suite 06 — Project Structure Deep Validation"

# We use bootstrap.py output (which = template contents) for fast structure checks
# This avoids running start.sh/init.py again

REQUIRED_ML_PACKAGES = [
    "pandas", "numpy", "scikit-learn", "joblib",
    "matplotlib", "seaborn", "fastapi", "uvicorn",
]

REQUIRED_DIRS_IN_BOOTSTRAP_OUTPUT = [
    "data", "models", "plots", "src", "deploy", "docs", "tests",
]

REQUIRED_FILES_IN_BOOTSTRAP_OUTPUT = [
    "CLAUDE.md",       # bootstrap writes CLAUDE.md (uppercase)
    "start.sh",
    "init.py",
    "requirements.txt",
    "README.md",
    # bootstrap.py and Dockerfile.bootstrap are distribution artifacts, not copied to project
    "src/CLAUDE.md",
    "deploy/CLAUDE.md",
    "docs/CLAUDE.md",
    "tests/CLAUDE.md",
    "docs/how_to_run.md",
    ".claude/settings.local.json",
    "data/.gitkeep",
    "models/.gitkeep",
    "plots/.gitkeep",
]

_bootstrap_output: Path = None
_bootstrap_error: str = None


def _ensure_bootstrap_output():
    global _bootstrap_output, _bootstrap_error
    if _bootstrap_output is not None or _bootstrap_error is not None:
        return

    import time
    tmp = Path(tempfile.mkdtemp(prefix="ml_struct_test_"))
    result = subprocess.run(
        ["python3", str(TEMPLATE_DIR / "bootstrap.py")],
        cwd=str(tmp),
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        _bootstrap_error = f"bootstrap.py failed (exit {result.returncode}): {result.stderr[:300]}"
        return
    out = tmp / "ml-pipeline-template"
    if not out.exists():
        _bootstrap_error = "ml-pipeline-template/ not created by bootstrap.py"
        return
    _bootstrap_output = out


def _test_all_required_files() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: all required files present", _bootstrap_error)
    missing = [f for f in REQUIRED_FILES_IN_BOOTSTRAP_OUTPUT if not (_bootstrap_output / f).exists()]
    if missing:
        return failresult(
            "Project: all required files present",
            f"{len(missing)} file(s) missing",
            details="\n".join(f"  MISSING: {f}" for f in missing),
        )
    return passresult("Project: all required files present",
                      f"{len(REQUIRED_FILES_IN_BOOTSTRAP_OUTPUT)} files verified")


def _test_all_required_dirs() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: all required dirs present", _bootstrap_error)
    missing = [d for d in REQUIRED_DIRS_IN_BOOTSTRAP_OUTPUT if not (_bootstrap_output / d).is_dir()]
    if missing:
        return failresult("Project: all required dirs present", f"Missing dirs: {missing}")
    return passresult("Project: all required dirs present",
                      f"{len(REQUIRED_DIRS_IN_BOOTSTRAP_OUTPUT)} dirs verified")


def _test_settings_local_json() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: .claude/settings.local.json valid", _bootstrap_error)
    p = _bootstrap_output / ".claude" / "settings.local.json"
    if not p.exists():
        return failresult("Project: .claude/settings.local.json valid", "File not found")
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        return failresult("Project: .claude/settings.local.json valid", f"Invalid JSON: {e}")
    allows = data.get("permissions", {}).get("allow", [])
    if len(allows) < 20:
        return failresult("Project: .claude/settings.local.json valid",
                          f"Only {len(allows)} permissions; expected >= 20")
    # Check no test artifacts remain
    bad = [a for a in allows if "/tmp/" in a or "private/tmp" in a]
    if bad:
        return failresult("Project: .claude/settings.local.json valid",
                          f"Test artifact paths found in permissions: {bad}")
    return passresult("Project: .claude/settings.local.json valid",
                      f"{len(allows)} clean permissions")


def _test_claude_md_content() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: CLAUDE.md content correct", _bootstrap_error)
    p = _bootstrap_output / "CLAUDE.md"
    content = p.read_text()
    required = [
        "ML Process Checklist",
        "Sub-Agent Routing",
        "random_state=42",
        ".ml_config.json",
        "Proceed with the pipeline? [Y/n]",
        "ONE question at a time" in content or "one-question-at-a-time" in content
            or "ONE question" in content,
    ]
    # all strings
    str_checks = required[:5]
    bool_check  = required[5]
    missing = [s for s in str_checks if s not in content]
    if missing or not bool_check:
        if not bool_check:
            missing.append("one-question-at-a-time init")
        return failresult("Project: CLAUDE.md content correct", f"Missing: {missing}")
    return passresult("Project: CLAUDE.md content correct")


def _test_src_claude_md_content() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: src/CLAUDE.md content correct", _bootstrap_error)
    p = _bootstrap_output / "src" / "CLAUDE.md"
    content = p.read_text()
    checks = [
        ("EDA Agent", "EDA Agent" in content),
        ("Data Engineering Agent", "Data Engineering Agent" in content),
        ("Optimization Agent", "Optimization Agent" in content),
        ("FastAPI Agent", "FastAPI Agent" in content),
        ("CoW-safe pandas", "CoW" in content or "df = df.assign" in content),
        ("X_train_raw.pkl", "X_train_raw.pkl" in content),
        ("solver saga", "solver='saga'" in content),
        ("Pipeline inspection", "named_steps" in content),
        ("learning_rate grid", "learning_rate" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("Project: src/CLAUDE.md content correct", f"Missing: {failed}")
    return passresult("Project: src/CLAUDE.md content correct",
                      f"All {len(checks)} content checks passed")


def _test_start_sh_executable() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: start.sh is executable", _bootstrap_error)
    sh = _bootstrap_output / "start.sh"
    if not sh.exists():
        return failresult("Project: start.sh is executable", "start.sh not found")
    if not sh.stat().st_mode & 0o111:
        return failresult("Project: start.sh is executable", "start.sh is NOT executable")
    return passresult("Project: start.sh is executable")


def _test_requirements_txt_packages() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: requirements.txt has all ML packages", _bootstrap_error)
    req = _bootstrap_output / "requirements.txt"
    if not req.exists():
        return failresult("Project: requirements.txt has all ML packages", "requirements.txt not found")
    content = req.read_text().lower()
    missing = [pkg for pkg in REQUIRED_ML_PACKAGES if pkg.lower() not in content]
    if missing:
        return failresult("Project: requirements.txt has all ML packages", f"Missing: {missing}")
    return passresult("Project: requirements.txt has all ML packages",
                      f"All {len(REQUIRED_ML_PACKAGES)} packages listed")


def _test_readme_non_empty() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: README.md is non-empty", _bootstrap_error)
    readme = _bootstrap_output / "README.md"
    if not readme.exists():
        return failresult("Project: README.md is non-empty", "README.md not found")
    content = readme.read_text().strip()
    if len(content) < 100:
        return failresult("Project: README.md is non-empty", f"README.md too short ({len(content)} chars)")
    return passresult("Project: README.md is non-empty", f"{len(content)} chars")


def _test_gitkeep_files() -> TestResult:
    _ensure_bootstrap_output()
    if _bootstrap_error:
        return failresult("Project: .gitkeep in empty dirs", _bootstrap_error)
    empty_dirs = ["data", "models", "plots"]
    missing = [d for d in empty_dirs if not (_bootstrap_output / d / ".gitkeep").exists()]
    if missing:
        return failresult("Project: .gitkeep in empty dirs",
                          f"Missing .gitkeep in: {missing}")
    return passresult("Project: .gitkeep in empty dirs",
                      f".gitkeep present in {len(empty_dirs)} empty dirs")


def run_suite() -> List[TestResult]:
    tests = [
        ("Project: all required files",            _test_all_required_files),
        ("Project: all required dirs",             _test_all_required_dirs),
        ("Project: settings.local.json clean",     _test_settings_local_json),
        ("Project: CLAUDE.md content",             _test_claude_md_content),
        ("Project: src/CLAUDE.md content",         _test_src_claude_md_content),
        ("Project: start.sh executable",           _test_start_sh_executable),
        ("Project: requirements.txt packages",     _test_requirements_txt_packages),
        ("Project: README.md non-empty",           _test_readme_non_empty),
        ("Project: .gitkeep in empty dirs",        _test_gitkeep_files),
    ]
    return [run_test(name, func) for name, func in tests]


if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
