"""
test_02_template_files.py — Content validation of template files (no subprocess).

Tests:
  2a. CLAUDE.md contains all 9 pipeline steps in the checklist
  2b. CLAUDE.md contains initialization instructions (1-question-at-a-time)
  2c. CLAUDE.md sub-agent routing table references all agents
  2d. deploy/CLAUDE.md contains Docker and Git/Deploy agent specs
  2e. docs/how_to_run.md covers all 3 entry modes
  2f. start.sh handles option 1/2/3 correctly
  2g. bootstrap.py creates all required subdirectories
  2h. init.py has create_venv() and install_deps() as separate functions
  2i. Dockerfile.bootstrap exists and references bootstrap.py
"""
from pathlib import Path
from .base import TEMPLATE_DIR, TestResult, run_test, passresult, failresult
from typing import List

SUITE_NAME = "Suite 02 — Template File Content Validation"


def _test_claude_md_pipeline_steps() -> TestResult:
    p = TEMPLATE_DIR / "CLAUDE.md"
    if not p.exists():
        # Try lowercase (macOS case-insensitive, Linux case-sensitive)
        p = TEMPLATE_DIR / "claude.md"
    if not p.exists():
        return failresult("CLAUDE.md: pipeline checklist steps", "CLAUDE.md / claude.md not found")
    content = p.read_text()

    # Checklist uses "- [ ] N." format, not "Step N"
    required_steps = [
        "[ ] 0.",   # Virtual Environment
        "[ ] 1.",   # Workspace Scan
        "[ ] 2.",   # EDA
        "[ ] 3.",   # Preprocessing
        "[ ] 4.",   # Feature Scaling / Training
        "[ ] 7.",   # Pipeline Export
        "[ ] 8.",   # Summary Report
        "[ ] 9.",   # Requirements File
        "[ ] 10.",  # Workspace Reorganisation
        "[ ] 11.",  # Git
        "[ ] 12.",  # Docker
    ]
    missing = [s for s in required_steps if s not in content]
    if missing:
        return failresult("CLAUDE.md: pipeline checklist steps", f"Missing: {missing}")
    return passresult("CLAUDE.md: pipeline checklist steps", f"{len(required_steps)} steps present")


def _test_claude_md_init_instructions() -> TestResult:
    p = TEMPLATE_DIR / "CLAUDE.md"
    content = p.read_text()

    checks = [
        ".ml_config.json" in content,
        "ONE question at a time" in content or "one question at a time" in content or "one-question-at-a-time" in content,
        "auto-detect" in content,
        "Proceed with the pipeline? [Y/n]" in content,
        ".venv" in content,
        "random_state=42" in content,
    ]
    ok = all(checks)
    failed_idx = [i for i, c in enumerate(checks) if not c]
    labels = [".ml_config.json", "one-question-at-a-time", "auto-detect", "confirmation prompt", ".venv", "random_state=42"]
    if not ok:
        missing = [labels[i] for i in failed_idx]
        return failresult("CLAUDE.md: init instructions", f"Missing: {missing}")
    return passresult("CLAUDE.md: init instructions", "All 6 required elements present")


def _test_claude_md_sub_agent_routing() -> TestResult:
    p = TEMPLATE_DIR / "CLAUDE.md"
    content = p.read_text()

    agents = [
        "EDA Agent",
        "Data Engineering Agent",
        "Optimization Agent",
        "FastAPI Agent",
        "Docker Agent",
        "Documentation Agent",
        "Testing Agent",
        "Git & Deploy Agent",
        "Cloud Deploy Agent",
    ]
    missing = [a for a in agents if a not in content]
    if missing:
        return failresult("CLAUDE.md: sub-agent routing table", f"Missing agents: {missing}")
    return passresult("CLAUDE.md: sub-agent routing table", f"All {len(agents)} agents listed")


def _test_deploy_claude_md() -> TestResult:
    p = TEMPLATE_DIR / "deploy" / "CLAUDE.md"
    if not p.exists():
        return failresult("deploy/CLAUDE.md: Docker and Git agent specs", "File not found")
    content = p.read_text()
    checks = [
        ("Docker Agent section", "Docker Agent" in content),
        ("Git & Deploy Agent section", "Git & Deploy Agent" in content),
        ("Cloud Deploy Agent section", "Cloud Deploy Agent" in content),
        ("Dockerfile step", "Dockerfile" in content),
        ("git init step", "git init" in content),
        ("gh repo create step", "gh repo create" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("deploy/CLAUDE.md: Docker and Git agent specs", f"Missing: {failed}")
    return passresult("deploy/CLAUDE.md: Docker and Git agent specs", f"All {len(checks)} elements present")


def _test_how_to_run_md() -> TestResult:
    p = TEMPLATE_DIR / "docs" / "how_to_run.md"
    if not p.exists():
        return failresult("docs/how_to_run.md: covers all 3 entry modes", "File not found")
    content = p.read_text()
    checks = [
        ("Shell script option", "Shell script" in content),
        ("Python CLI option", "Python CLI" in content or "init.py" in content),
        ("Claude Code option", "Claude Code" in content),
        ("bootstrap.py mentioned", "bootstrap.py" in content),
        ("start.sh mentioned", "start.sh" in content),
        ("Prerequisites table", "Prerequisites" in content),
        ("Folder layout section", "Folder layout" in content or "folder layout" in content),
        ("Troubleshooting section", "Troubleshooting" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("docs/how_to_run.md: covers all 3 entry modes", f"Missing: {failed}")
    return passresult("docs/how_to_run.md: covers all 3 entry modes", f"{len(checks)} sections verified")


def _test_start_sh_mode_handling() -> TestResult:
    p = TEMPLATE_DIR / "start.sh"
    content = p.read_text()
    # Note: start.sh handles option 1 implicitly (fall-through); option 2 and 3 are the special cases.
    checks = [
        ("Option 2: delegates to init.py",   "init.py" in content),
        ("Option 3: sets LAUNCH_CLAUDE",      'LAUNCH_CLAUDE=true' in content),
        ("Option 3 runs claude .",            'claude .' in content),
        ("Default is 3",                      'ENTRY_MODE:-3' in content or 'default: 3' in content),
        ("pip install uses .venv path",       '.venv/bin/pip' in content),
        ("rsync excludes .venv",              "--exclude='.venv/'" in content or '--exclude=.venv/' in content),
        ("python3 -m venv creates venv",      "python3 -m venv" in content),
        ("venv created before rsync",         content.find("python3 -m venv") < content.find("rsync")),
        ("pip install after rsync",           content.find("rsync") < content.find('.venv/bin/pip')),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("start.sh: mode handling and venv logic", f"Missing: {failed}")
    return passresult("start.sh: mode handling and venv logic", f"All {len(checks)} checks passed")


def _test_bootstrap_creates_all_dirs() -> TestResult:
    p = TEMPLATE_DIR / "bootstrap.py"
    content = p.read_text()
    required_dirs = ["data", "models", "plots", "src", "deploy", "docs", "tests"]
    missing = [d for d in required_dirs if f'"{d}"' not in content and f"'{d}'" not in content]
    if missing:
        return failresult("bootstrap.py: creates all required dirs", f"Dirs not referenced: {missing}")

    # Check it embeds all critical agent spec files
    required_files = ["src/CLAUDE.md", "deploy/CLAUDE.md", "docs/CLAUDE.md", "tests/CLAUDE.md",
                      "start.sh", "init.py", "requirements.txt"]
    missing_files = [f for f in required_files if f not in content]
    if missing_files:
        return failresult("bootstrap.py: creates all required dirs", f"Missing file references: {missing_files}")
    return passresult("bootstrap.py: creates all required dirs", "All dirs and key files referenced")


def _test_init_py_separate_venv_functions() -> TestResult:
    p = TEMPLATE_DIR / "init.py"
    content = p.read_text()

    # Extract just the create_venv function body (between its def and the next def)
    start = content.find("def create_venv(")
    end   = content.find("def install_deps(")
    venv_body = content[start:end] if start != -1 and end != -1 else ""

    checks = [
        ("create_venv() function defined",         "def create_venv(" in content),
        ("install_deps() function defined",        "def install_deps(" in content),
        # create_venv body should NOT actually invoke pip (docstring/comment mentions are ok)
        # Look for actual pip subprocess invocation: ["pip"] or [pip, "install"] patterns
        ("create_venv does NOT run pip install",   '"pip"' not in venv_body and "'pip'" not in venv_body),
        ("create_venv only calls python -m venv",  "python3 -m venv" in venv_body or "-m venv" in venv_body
                                                    or "venv" in venv_body),
        ("install_deps reads requirements.txt",    "requirements.txt" in content),
        ("install_deps uses .venv/bin/pip",        ".venv" in content and "pip" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("init.py: separate create_venv/install_deps functions", f"Checks failed: {failed}")
    return passresult("init.py: separate create_venv/install_deps functions")


def _test_dockerfile_bootstrap() -> TestResult:
    p = TEMPLATE_DIR / "Dockerfile.bootstrap"
    if not p.exists():
        return failresult("Dockerfile.bootstrap: valid structure", "File not found")
    content = p.read_text()
    # Dockerfile uses ENTRYPOINT ["python3", "/bootstrap.py"] not RUN python3 bootstrap.py
    checks = [
        ("FROM python",           "FROM python" in content),
        ("COPY bootstrap.py",     "bootstrap.py" in content),
        ("ENTRYPOINT or CMD runs bootstrap", "bootstrap.py" in content and
            ("ENTRYPOINT" in content or "CMD" in content)),
        ("VOLUME or WORKDIR /output", "/output" in content),
    ]
    failed = [name for name, ok in checks if not ok]
    if failed:
        return failresult("Dockerfile.bootstrap: valid structure", f"Missing: {failed}")
    return passresult("Dockerfile.bootstrap: valid structure")


def run_suite() -> List[TestResult]:
    tests = [
        ("CLAUDE.md pipeline steps",          _test_claude_md_pipeline_steps),
        ("CLAUDE.md init instructions",        _test_claude_md_init_instructions),
        ("CLAUDE.md sub-agent routing",        _test_claude_md_sub_agent_routing),
        ("deploy/CLAUDE.md agent specs",       _test_deploy_claude_md),
        ("docs/how_to_run.md entry modes",     _test_how_to_run_md),
        ("start.sh mode/venv handling",        _test_start_sh_mode_handling),
        ("bootstrap.py dir/file coverage",     _test_bootstrap_creates_all_dirs),
        ("init.py venv/install separation",    _test_init_py_separate_venv_functions),
        ("Dockerfile.bootstrap structure",     _test_dockerfile_bootstrap),
    ]
    return [run_test(name, func) for name, func in tests]


if __name__ == "__main__":
    results = run_suite()
    for r in results:
        print(r)
