"""
base.py — Shared infrastructure for template test suites.
"""
import os, sys, shutil, subprocess, tempfile, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Callable, Optional

# ── Paths ──────────────────────────────────────────────────────────────
# tests/template_tests/suites/ → tests/template_tests/ → tests/ → project_root
SUITE_DIR    = Path(__file__).parent
TESTS_DIR    = SUITE_DIR.parent
FIXTURES_DIR = TESTS_DIR / "fixtures"
RESULTS_DIR  = TESTS_DIR / "results"
TEMPLATE_DIR = TESTS_DIR.parent.parent   # .../Test-ML/

# ── Colours ────────────────────────────────────────────────────────────
G = "\033[0;32m"   # green
R = "\033[0;31m"   # red
Y = "\033[1;33m"   # yellow
C = "\033[0;36m"   # cyan
B = "\033[1m"      # bold
X = "\033[0m"      # reset

# ── Required template files (relative to TEMPLATE_DIR) ────────────────
REQUIRED_TEMPLATE_FILES = [
    "CLAUDE.md",           # uppercase — bootstrap writes CLAUDE.md; macOS is case-insensitive
    "start.sh",
    "init.py",
    "bootstrap.py",
    "requirements.txt",
    "README.md",
    "Dockerfile.bootstrap",
    "src/CLAUDE.md",
    "deploy/CLAUDE.md",
    "docs/CLAUDE.md",
    "tests/CLAUDE.md",
    "docs/how_to_run.md",
    ".claude/settings.local.json",
]

# Required top-level dirs in template
REQUIRED_TEMPLATE_DIRS = ["src", "deploy", "docs", "tests", "data", "models", "plots"]

# Required dirs in a created project
REQUIRED_PROJECT_DIRS = ["data", "models", "plots", "src", "deploy", "docs", "tests", ".venv"]

# Required files in a created project (relative to project root).
# Setup scripts (bootstrap.py, Dockerfile.bootstrap, start.sh, init.py) are
# intentionally excluded from projects — running them inside a project creates
# nested templates or duplicate sibling projects (the root cause of duplication).
REQUIRED_PROJECT_FILES = [
    "CLAUDE.md",
    "requirements.txt",
    "README.md",
    ".ml_config.json",
    "src/CLAUDE.md",
    "deploy/CLAUDE.md",
    "docs/CLAUDE.md",
    "tests/CLAUDE.md",
    ".claude/settings.local.json",
]

# Keys that .ml_config.json must contain
ML_CONFIG_REQUIRED_KEYS = [
    "project_name",
    "dataset_filename",
    "dataset_path",
    "target_column",
    "task_type",
    "deployment_platform",
    "github_username",
    "github_repo",
    "github_visibility",
    "python_version",
    "created_at",
    "venv_path",
    "template_version",
]


# ── TestResult ─────────────────────────────────────────────────────────
@dataclass
class TestResult:
    name: str
    passed: bool = False
    skipped: bool = False
    skip_reason: str = ""
    message: str = ""
    details: str = ""
    duration: float = 0.0

    @property
    def status(self) -> str:
        if self.skipped:
            return "SKIP"
        return "PASS" if self.passed else "FAIL"

    @property
    def colour(self) -> str:
        if self.skipped:
            return Y
        return G if self.passed else R

    def __str__(self) -> str:
        dur = f"  ({self.duration:.1f}s)" if self.duration >= 0.5 else ""
        base = f"  {self.colour}[{self.status}]{X} {self.name}{dur}"
        if not self.passed and not self.skipped and self.message:
            base += f"\n        {R}→ {self.message}{X}"
        if not self.passed and not self.skipped and self.details:
            for line in self.details.strip().split("\n"):
                base += f"\n          {line}"
        return base


def skip(name: str, reason: str) -> TestResult:
    """Return a skipped test result."""
    return TestResult(name=name, skipped=True, skip_reason=reason)


def passresult(name: str, msg: str = "", duration: float = 0.0) -> TestResult:
    return TestResult(name=name, passed=True, message=msg, duration=duration)


def failresult(name: str, msg: str, details: str = "", duration: float = 0.0) -> TestResult:
    return TestResult(name=name, passed=False, message=msg, details=details, duration=duration)


# ── Test runner helpers ────────────────────────────────────────────────
def run_test(name: str, func: Callable[[], TestResult]) -> TestResult:
    """Run a single test function, catching all exceptions."""
    start = time.time()
    try:
        result = func()
        result.duration = time.time() - start
        return result
    except AssertionError as e:
        return TestResult(name=name, passed=False, message=str(e), duration=time.time() - start)
    except Exception as e:
        return TestResult(
            name=name, passed=False,
            message=f"Unexpected error: {type(e).__name__}: {e}",
            duration=time.time() - start
        )


# ── Temp project setup ─────────────────────────────────────────────────
EXCLUDE_COPY = {
    ".git", "__pycache__", ".venv", ".DS_Store",
    ".ml_config.json",
}
EXCLUDE_EXTS = {".csv", ".pkl", ".npy", ".png", ".pyc"}


def copy_template_to_temp() -> Path:
    """
    Copy the template (without .venv, data, models, etc.) to a temp directory.
    Returns the path to the temp copy of the template.
    """
    tmp_root = Path(tempfile.mkdtemp(prefix="ml_tmpl_test_"))
    tmpl_copy = tmp_root / "Test-ML"

    def ignore_fn(src: str, names: list) -> set:
        ignored = set()
        for name in names:
            full = Path(src) / name
            if name in EXCLUDE_COPY:
                ignored.add(name)
            elif full.suffix in EXCLUDE_EXTS:
                ignored.add(name)
        return ignored

    shutil.copytree(str(TEMPLATE_DIR), str(tmpl_copy), ignore=ignore_fn)
    return tmpl_copy


def make_fake_claude_bin(tmp_dir: Path) -> Path:
    """
    Create a fake 'claude' executable that immediately exits 0.
    Returns the bin directory to prepend to PATH.
    """
    bin_dir = tmp_dir / "fake_bin"
    bin_dir.mkdir(exist_ok=True)
    claude_fake = bin_dir / "claude"
    claude_fake.write_text('#!/bin/bash\necho "[TEST-MOCK] claude . invoked — skipping in test"\nexit 0\n')
    claude_fake.chmod(0o755)
    return bin_dir


def find_created_project(parent_dir: Path, project_name: str, after_time: float) -> Optional[Path]:
    """
    Find a project directory created after 'after_time' whose name starts with project_name.

    NOTE: We parse the embedded timestamp from the directory name
    (format PROJECT_NAME_YYYYMMDD_HHMMSS) instead of relying on st_birthtime.
    On macOS APFS, shutil.copytree preserves the SOURCE directory's birthtime,
    so the copied template tree inherits old birthtimes — making st_birthtime
    unreliable as a "was this just created?" signal.
    """
    from datetime import datetime
    for candidate in parent_dir.iterdir():
        if not candidate.is_dir():
            continue
        if not candidate.name.startswith(project_name):
            continue
        # Primary: parse YYYYMMDD_HHMMSS suffix from the directory name
        suffix = candidate.name[len(project_name):]   # e.g. "_20260525_004534"
        if suffix.startswith("_"):
            suffix = suffix[1:]  # "20260525_004534"
        try:
            # strptime without tzinfo → local time; .timestamp() converts to epoch correctly
            ts = datetime.strptime(suffix, "%Y%m%d_%H%M%S").timestamp()
            # Accept if the embedded timestamp is within the test window (≥ after_time - 60s)
            if ts >= after_time - 60:
                return candidate
            continue
        except ValueError:
            pass
        # Fallback: filesystem times (less reliable on APFS CoW clones)
        try:
            btime = candidate.stat().st_birthtime
        except AttributeError:
            btime = candidate.stat().st_mtime
        if btime >= after_time - 2.0:
            return candidate
    return None
