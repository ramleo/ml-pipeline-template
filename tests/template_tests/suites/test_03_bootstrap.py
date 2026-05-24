"""
test_03_bootstrap.py — Run bootstrap.py and verify output (subprocess tests).

Tests:
  3a. python3 bootstrap.py → creates ml-pipeline-template/ in CWD
  3b. All required subdirectories created
  3c. All required files written
  3d. start.sh is executable in output
  3e. Custom folder name: python3 bootstrap.py custom-name
  3f. Error on already-existing folder (exit code != 0)
  3g. Files in output match source (spot-check CLAUDE.md)
"""
import os, subprocess, shutil, tempfile, json
from pathlib import Path
from typing import List
from .base import (
    TEMPLATE_DIR, REQUIRED_TEMPLATE_DIRS, REQUIRED_TEMPLATE_FILES,
    TestResult, run_test, passresult, failresult, skip
)

SUITE_NAME = "Suite 03 — bootstrap.py Behaviour"

BOOTSTRAP_EXPECTED_DIRS = ["data", "models", "plots", "src", "deploy", "docs", "tests"]
BOOTSTRAP_EXPECTED_FILES = [
    "CLAUDE.md",       # bootstrap writes CLAUDE.md (uppercase)
    "start.sh",
    "init.py",
    # bootstrap.py does NOT copy itself — that would be meta/circular
    "requirements.txt",
    "README.md",
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


def _run_bootstrap(cwd: Path, folder_name: str = None, timeout: int = 60) -> subprocess.CompletedProcess:
    cmd = ["python3", str(TEMPLATE_DIR / "bootstrap.py")]
    if folder_name:
        cmd.append(folder_name)
    return subprocess.run(
        cmd, cwd=str(cwd),
        capture_output=True, text=True, timeout=timeout
    )


def _test_bootstrap_creates_template() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_test_") as tmp:
        tmp_path = Path(tmp)
        result = _run_bootstrap(tmp_path)

        if result.returncode != 0:
            return failresult(
                "bootstrap.py creates ml-pipeline-template/",
                f"Exit code {result.returncode}",
                details=result.stderr[:500] if result.stderr else result.stdout[:500],
            )

        out_dir = tmp_path / "ml-pipeline-template"
        if not out_dir.exists():
            return failresult(
                "bootstrap.py creates ml-pipeline-template/",
                "ml-pipeline-template/ directory was not created",
                details=result.stdout[:300],
            )
        return passresult("bootstrap.py creates ml-pipeline-template/", str(out_dir))


def _test_bootstrap_creates_subdirs() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_dirs_") as tmp:
        tmp_path = Path(tmp)
        _run_bootstrap(tmp_path)
        out_dir = tmp_path / "ml-pipeline-template"
        if not out_dir.exists():
            return failresult("bootstrap.py: all subdirs created", "ml-pipeline-template/ not found — 3a likely failed")

        missing = [d for d in BOOTSTRAP_EXPECTED_DIRS if not (out_dir / d).is_dir()]
        if missing:
            return failresult("bootstrap.py: all subdirs created", f"Missing dirs: {missing}")
        return passresult("bootstrap.py: all subdirs created", f"{len(BOOTSTRAP_EXPECTED_DIRS)} dirs present")


def _test_bootstrap_creates_files() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_files_") as tmp:
        tmp_path = Path(tmp)
        _run_bootstrap(tmp_path)
        out_dir = tmp_path / "ml-pipeline-template"
        if not out_dir.exists():
            return failresult("bootstrap.py: all required files written", "ml-pipeline-template/ not found")

        missing = [f for f in BOOTSTRAP_EXPECTED_FILES if not (out_dir / f).exists()]
        if missing:
            return failresult(
                "bootstrap.py: all required files written",
                f"{len(missing)} file(s) missing",
                details="\n".join(f"  MISSING: {f}" for f in missing),
            )
        return passresult("bootstrap.py: all required files written", f"{len(BOOTSTRAP_EXPECTED_FILES)} files present")


def _test_bootstrap_start_sh_executable() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_exec_") as tmp:
        tmp_path = Path(tmp)
        _run_bootstrap(tmp_path)
        out_dir = tmp_path / "ml-pipeline-template"
        sh = out_dir / "start.sh"
        if not sh.exists():
            return failresult("bootstrap.py: start.sh is executable", "start.sh not found in output")
        if not sh.stat().st_mode & 0o111:
            return failresult("bootstrap.py: start.sh is executable", "start.sh exists but is NOT executable")
        return passresult("bootstrap.py: start.sh is executable")


def _test_bootstrap_custom_name() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_custom_") as tmp:
        tmp_path = Path(tmp)
        result = _run_bootstrap(tmp_path, folder_name="my-custom-template")
        if result.returncode != 0:
            return failresult(
                "bootstrap.py: custom folder name",
                f"Exit code {result.returncode}",
                details=result.stderr[:300],
            )
        out_dir = tmp_path / "my-custom-template"
        if not out_dir.exists():
            return failresult("bootstrap.py: custom folder name", "my-custom-template/ not created")
        # Ensure default name was NOT created
        default_dir = tmp_path / "ml-pipeline-template"
        if default_dir.exists():
            return failresult("bootstrap.py: custom folder name", "Default ml-pipeline-template/ also created (unexpected)")
        return passresult("bootstrap.py: custom folder name", f"Created: {out_dir.name}/")


def _test_bootstrap_error_on_existing_folder() -> TestResult:
    with tempfile.TemporaryDirectory(prefix="ml_bs_exist_") as tmp:
        tmp_path = Path(tmp)
        # Create the folder first
        (tmp_path / "ml-pipeline-template").mkdir()
        result = _run_bootstrap(tmp_path)
        if result.returncode == 0:
            return failresult(
                "bootstrap.py: errors on existing folder",
                "Expected non-zero exit code when folder already exists, but got 0"
            )
        if "already exists" not in result.stdout and "already exists" not in result.stderr:
            return failresult(
                "bootstrap.py: errors on existing folder",
                "Expected 'already exists' error message",
                details=result.stdout[:200],
            )
        return passresult("bootstrap.py: errors on existing folder", "Correct error message and exit code != 0")


def _test_bootstrap_settings_json_valid() -> TestResult:
    """Check that the .claude/settings.local.json written by bootstrap is valid."""
    with tempfile.TemporaryDirectory(prefix="ml_bs_json_") as tmp:
        tmp_path = Path(tmp)
        _run_bootstrap(tmp_path)
        settings = tmp_path / "ml-pipeline-template" / ".claude" / "settings.local.json"
        if not settings.exists():
            return failresult("bootstrap.py: .claude/settings.local.json valid JSON", "File not found in output")
        try:
            data = json.loads(settings.read_text())
        except Exception as e:
            return failresult("bootstrap.py: .claude/settings.local.json valid JSON", f"Invalid JSON: {e}")
        if "permissions" not in data or "allow" not in data["permissions"]:
            return failresult("bootstrap.py: .claude/settings.local.json valid JSON", "Missing permissions.allow key")
        allows = data["permissions"]["allow"]
        if len(allows) < 20:
            return failresult("bootstrap.py: .claude/settings.local.json valid JSON",
                              f"Expected >= 20 entries, found {len(allows)}")
        return passresult("bootstrap.py: .claude/settings.local.json valid JSON",
                          f"{len(allows)} permissions written")


def run_suite() -> List[TestResult]:
    tests = [
        ("bootstrap creates ml-pipeline-template/",   _test_bootstrap_creates_template),
        ("bootstrap creates all subdirs",              _test_bootstrap_creates_subdirs),
        ("bootstrap creates all required files",       _test_bootstrap_creates_files),
        ("bootstrap start.sh is executable",           _test_bootstrap_start_sh_executable),
        ("bootstrap custom folder name",               _test_bootstrap_custom_name),
        ("bootstrap error on existing folder",         _test_bootstrap_error_on_existing_folder),
        ("bootstrap settings.local.json valid",        _test_bootstrap_settings_json_valid),
    ]
    return [run_test(name, func) for name, func in tests]


if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
