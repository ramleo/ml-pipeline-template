"""
test_01_prerequisites.py — Static prerequisite checks (no subprocess).

Tests:
  1a. Python version >= 3.9
  1b. start.sh is executable
  1c. All required template files exist
  1d. All required template directories exist
  1e. .claude/settings.local.json is valid JSON
  1f. requirements.txt contains required ML packages
"""
import json, sys
from pathlib import Path
from typing import List
from .base import (
    TEMPLATE_DIR, REQUIRED_TEMPLATE_FILES, REQUIRED_TEMPLATE_DIRS,
    TestResult, run_test, passresult, failresult, skip
)

SUITE_NAME = "Suite 01 — Prerequisites & Template Integrity"

REQUIRED_PACKAGES = [
    "pandas", "numpy", "scikit-learn", "joblib",
    "matplotlib", "seaborn", "fastapi", "uvicorn",
]

ML_CONFIG_REQUIRED_KEYS = [
    "project_name", "dataset_filename", "dataset_path",
    "target_column", "task_type", "deployment_platform",
    "github_username", "github_repo", "github_visibility",
    "python_version", "created_at", "venv_path", "template_version",
]

SRC_CLAUDE_AGENT_SECTIONS = [
    "EDA Agent",
    "Data Engineering Agent",
    "Optimization Agent",
    "FastAPI Agent",
    "Step 8",
    "Step 9",
    "Step 10",
]

SETTINGS_REQUIRED_PREFIXES = [
    "Bash(.venv/bin/pip",
    "Bash(.venv/bin/python",
    "Bash(python3",
    "Bash(git",
    "Bash(curl",
    "Bash(mkdir",
]


def _test_python_version() -> TestResult:
    v = sys.version_info
    if v >= (3, 9):
        return passresult("Python >= 3.9", f"Found Python {v.major}.{v.minor}.{v.micro}")
    return failresult("Python >= 3.9", f"Python {v.major}.{v.minor} found — requires 3.9+")


def _test_start_sh_executable() -> TestResult:
    p = TEMPLATE_DIR / "start.sh"
    if not p.exists():
        return failresult("start.sh exists and is executable", "start.sh not found in template root")
    if not p.stat().st_mode & 0o111:
        return failresult("start.sh exists and is executable", "start.sh exists but is NOT executable")
    return passresult("start.sh exists and is executable")


def _test_required_template_files() -> TestResult:
    missing = []
    for f in REQUIRED_TEMPLATE_FILES:
        if not (TEMPLATE_DIR / f).exists():
            missing.append(f)
    if missing:
        return failresult(
            "All required template files present",
            f"{len(missing)} file(s) missing",
            details="\n".join(f"  MISSING: {f}" for f in missing),
        )
    return passresult("All required template files present", f"{len(REQUIRED_TEMPLATE_FILES)} files checked")


def _test_required_template_dirs() -> TestResult:
    missing = []
    for d in REQUIRED_TEMPLATE_DIRS:
        if not (TEMPLATE_DIR / d).is_dir():
            missing.append(d)
    if missing:
        return failresult(
            "All required template directories present",
            f"{len(missing)} director(ies) missing",
            details="\n".join(f"  MISSING: {d}/" for d in missing),
        )
    return passresult("All required template directories present", f"{len(REQUIRED_TEMPLATE_DIRS)} dirs checked")


def _test_settings_local_json() -> TestResult:
    p = TEMPLATE_DIR / ".claude" / "settings.local.json"
    if not p.exists():
        return failresult(".claude/settings.local.json is valid JSON", "File does not exist")
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return failresult(".claude/settings.local.json is valid JSON", f"Invalid JSON: {e}")

    if "permissions" not in data:
        return failresult(".claude/settings.local.json is valid JSON", "Missing 'permissions' key")
    if "allow" not in data["permissions"]:
        return failresult(".claude/settings.local.json is valid JSON", "Missing 'permissions.allow' key")

    allows = data["permissions"]["allow"]
    if not isinstance(allows, list) or len(allows) < 20:
        return failresult(
            ".claude/settings.local.json is valid JSON",
            f"Expected >= 20 allow entries, found {len(allows)}"
        )

    # Check required permission prefixes
    missing = []
    for prefix in SETTINGS_REQUIRED_PREFIXES:
        if not any(a.startswith(prefix) for a in allows):
            missing.append(prefix)
    if missing:
        return failresult(
            ".claude/settings.local.json is valid JSON",
            f"Missing expected permission prefixes: {missing}",
        )

    return passresult(".claude/settings.local.json is valid JSON", f"{len(allows)} permissions defined")


def _test_requirements_txt() -> TestResult:
    p = TEMPLATE_DIR / "requirements.txt"
    if not p.exists():
        return failresult("requirements.txt contains required ML packages", "File not found")

    content = p.read_text().lower()
    missing = [pkg for pkg in REQUIRED_PACKAGES if pkg.lower() not in content]

    if missing:
        return failresult(
            "requirements.txt contains required ML packages",
            f"Missing packages: {missing}",
        )
    return passresult("requirements.txt contains required ML packages", f"{len(REQUIRED_PACKAGES)} packages found")


def _test_src_claude_md_sections() -> TestResult:
    p = TEMPLATE_DIR / "src" / "CLAUDE.md"
    if not p.exists():
        return failresult("src/CLAUDE.md contains all agent specs", "src/CLAUDE.md not found")

    content = p.read_text()
    missing = [s for s in SRC_CLAUDE_AGENT_SECTIONS if s not in content]
    if missing:
        return failresult(
            "src/CLAUDE.md contains all agent specs",
            f"Missing sections: {missing}",
        )

    # Verify critical preprocessing rules
    checks = [
        ("CoW-safe pandas", "df = df.assign" in content or "CoW" in content),
        ("X_train_raw.pkl mentioned", "X_train_raw.pkl" in content),
        ("X_test_raw.pkl mentioned", "X_test_raw.pkl" in content),
        ("preprocessor.pkl mentioned", "preprocessor.pkl" in content),
        ("solver='saga'", "solver='saga'" in content),
        ("GradientBoostingClassifier grid", "learning_rate" in content),
        ("Pipeline inspection step", "named_steps" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult(
            "src/CLAUDE.md contains all agent specs",
            f"Missing critical content: {failed}",
        )
    return passresult("src/CLAUDE.md contains all agent specs", f"{len(SRC_CLAUDE_AGENT_SECTIONS)} sections verified")


def _test_start_sh_staging_order() -> TestResult:
    """Verify start.sh uses staging approach: rsync → venv → pip → atomic mv."""
    p = TEMPLATE_DIR / "start.sh"
    content = p.read_text()

    staging_pos = content.find("STAGING_DIR=")
    rsync_pos   = content.find("rsync")
    venv_pos    = content.find("python3 -m venv")
    pip_pos     = content.find('bin/pip" install -r')
    mv_pos      = content.find('mv "$STAGING_DIR"')

    checks = [
        ("STAGING_DIR defined",    staging_pos != -1),
        ("rsync present",          rsync_pos != -1),
        ("venv creation present",  venv_pos != -1),
        ("pip install present",    pip_pos != -1),
        ("atomic mv present",      mv_pos != -1),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("start.sh: staging order (rsync→venv→pip→mv)", f"Missing: {failed}")

    if not (rsync_pos < venv_pos):
        return failresult(
            "start.sh: staging order (rsync→venv→pip→mv)",
            f"rsync (pos {rsync_pos}) is NOT before venv (pos {venv_pos}) — staging order broken"
        )
    if not (venv_pos < pip_pos):
        return failresult(
            "start.sh: staging order (rsync→venv→pip→mv)",
            f"venv (pos {venv_pos}) is NOT before pip (pos {pip_pos})"
        )
    if not (pip_pos < mv_pos):
        return failresult(
            "start.sh: staging order (rsync→venv→pip→mv)",
            f"pip (pos {pip_pos}) is NOT before mv (pos {mv_pos})"
        )
    return passresult("start.sh: staging order (rsync→venv→pip→mv)", "rsync → venv → pip → mv ✓")


def _test_init_py_staging_order() -> TestResult:
    """Verify init.py __main__ uses staging: copy_template → create_venv → install_deps → move_to_final."""
    p = TEMPLATE_DIR / "init.py"
    content = p.read_text()

    copy_tmpl_pos    = content.rfind("copy_template(")
    create_venv_pos  = content.rfind("create_venv(")
    install_deps_pos = content.rfind("install_deps(")
    move_final_pos   = content.rfind("move_to_final(")

    checks = [
        ("copy_template() call present",  copy_tmpl_pos != -1),
        ("create_venv() call present",    create_venv_pos != -1),
        ("install_deps() call present",   install_deps_pos != -1),
        ("move_to_final() call present",  move_final_pos != -1),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("init.py: staging order (copy→venv→install→move)", f"Missing: {failed}")

    if not (copy_tmpl_pos < create_venv_pos):
        return failresult(
            "init.py: staging order (copy→venv→install→move)",
            f"copy_template at {copy_tmpl_pos} is NOT before create_venv at {create_venv_pos}"
        )
    if not (create_venv_pos < install_deps_pos):
        return failresult(
            "init.py: staging order (copy→venv→install→move)",
            f"create_venv at {create_venv_pos} is NOT before install_deps at {install_deps_pos}"
        )
    if not (install_deps_pos < move_final_pos):
        return failresult(
            "init.py: staging order (copy→venv→install→move)",
            f"install_deps at {install_deps_pos} is NOT before move_to_final at {move_final_pos}"
        )
    return passresult("init.py: staging order (copy→venv→install→move)",
                      "copy_template → create_venv → install_deps → move_to_final ✓")


def run_suite() -> List[TestResult]:
    tests = [
        ("Python >= 3.9",                         _test_python_version),
        ("start.sh executable",                   _test_start_sh_executable),
        ("Required template files",               _test_required_template_files),
        ("Required template dirs",                _test_required_template_dirs),
        (".claude/settings.local.json valid",     _test_settings_local_json),
        ("requirements.txt packages",             _test_requirements_txt),
        ("src/CLAUDE.md agent specs",             _test_src_claude_md_sections),
        ("start.sh staging order",                 _test_start_sh_staging_order),
        ("init.py staging order",                  _test_init_py_staging_order),
    ]
    return [run_test(name, func) for name, func in tests]


# Allow running directly
if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
