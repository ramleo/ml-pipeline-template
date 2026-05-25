# ML Pipeline Template — Bootstrap System Reconstruction Spec

**Version:** 1.0.0  
**Purpose:** Complete specification for recreating the ML Pipeline Template bootstrap system from scratch and publishing it to GitHub.  
**Audience:** AI agent or developer who must rebuild this system without access to the original source.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [bootstrap.py Architecture](#3-bootstrappy-architecture)
4. [start.sh Architecture](#4-startsh-architecture)
5. [init.py Architecture](#5-initpy-architecture)
6. [.ml_config.json — Required Keys](#6-ml_configjson--required-keys)
7. [CLAUDE.md Agent System](#7-claudemd-agent-system)
8. [Project vs Template Distinction](#8-project-vs-template-distinction)
9. [GitHub Setup Steps](#9-github-setup-steps)
10. [requirements.txt — Pinned Versions](#10-requirementstxt--pinned-versions)
11. [.claude/settings.local.json](#11-claudesettingslocaljson)
12. [Common Pitfalls to Avoid](#12-common-pitfalls-to-avoid)

---

## 1. Project Overview

### What This Template Does

The ML Pipeline Template is an autonomous, end-to-end machine learning scaffold powered by Claude Code. A user downloads a single Python file (`bootstrap.py`), runs it, answers a few prompts, and gets a fully wired project folder with:

- A Python virtual environment (`.venv/`) with all dependencies pre-installed
- A `.ml_config.json` configuration file pre-populated with their choices
- A CLAUDE.md agent system that directs Claude Code through 15 steps (EDA, preprocessing, training, API, Docker, deploy)
- All required subdirectory `CLAUDE.md` files for sub-agent delegation

### User-Facing Flow

```
curl -O https://raw.githubusercontent.com/<username>/ml-pipeline-template/main/bootstrap.py
python3 bootstrap.py
# → answers prompts (project name, CSV path, platform, GitHub)
# → project created at ./<project_name>_TIMESTAMP/
# → .venv created and deps installed inside it
# → claude . launched automatically
```

**Critical design point:** `bootstrap.py` creates the project folder directly in the current working directory. There is NO intermediate `ml-pipeline-template/` folder created when using `bootstrap.py`. The project appears once, fully formed.

The template repo itself (on GitHub) provides two additional entry points for users who clone the repo rather than using `bootstrap.py`:
- `start.sh` — bash wizard that creates a sibling project folder
- `init.py` — Python equivalent of `start.sh`

Both `start.sh` and `init.py` run from INSIDE the cloned template folder and create the project as a SIBLING directory (not inside the template folder).

### Deployment Platforms Supported

| Choice | Platform | Config File |
|---|---|---|
| 1 | Ask me later | — |
| 2 | Render (recommended free tier) | `render.yaml` |
| 3 | Fly.io | `fly.toml` |
| 4 | Railway | `railway.toml` |
| 5 | AWS App Runner | `apprunner.yaml` |
| 6 | GCP Cloud Run | — |
| 7 | Azure Container Apps | — |
| 8 | Skip / local / Docker only | — |

---

## 2. Repository Structure

The GitHub repository root is the template source. Every file listed here must exist in the repo.

```
ml-pipeline-template/              ← GitHub repo root
├── bootstrap.py                   ← single-file installer (main entry point)
├── Dockerfile.bootstrap           ← Docker alternative to bootstrap.py
├── start.sh                       ← bash wizard (runs INSIDE template folder)
├── init.py                        ← Python wizard (runs INSIDE template folder)
├── CLAUDE.md                      ← root agent instructions (always loaded)
├── requirements.txt               ← pinned ML dependencies
├── README.md                      ← project readme with bootstrap curl URL
├── .gitignore                     ← Python / macOS / IDE / secrets
├── .ml_config.json.example        ← reference config template (not .ml_config.json)
├── .claude/
│   └── settings.local.json        ← pre-authorized bash commands for Claude Code
├── src/
│   └── CLAUDE.md                  ← EDA, Data Engineering, Optimization, FastAPI specs
├── deploy/
│   ├── CLAUDE.md                  ← Docker, Git & Deploy, Cloud Deploy specs + Steps 11–12
│   ├── cloud.md                   ← index: @-imports cloud-render.md + cloud-platforms.md
│   ├── cloud-render.md            ← Step 13 — Render deployment
│   └── cloud-platforms.md        ← Step 14 — AWS, GCP, Azure, Fly.io, Railway
├── docs/
│   ├── CLAUDE.md                  ← Documentation agent spec
│   ├── how_to_run.md              ← step-by-step usage guide
│   └── claude_structure.md        ← CLAUDE.md split structure reference
├── tests/
│   └── CLAUDE.md                  ← Testing agent spec
├── data/
│   └── .gitkeep                   ← preserves empty directory in git
├── models/
│   └── .gitkeep
└── plots/
    └── .gitkeep
```

### Files That Must NOT Be Committed to the Template Repo

- `.ml_config.json` — user-specific, auto-generated at project creation time
- `data/*.csv`, `models/*.pkl`, `models/*.npy`, `plots/*.png` — runtime artifacts
- `.venv/` — generated locally

The `.gitignore` must exclude all of these.

---

## 3. bootstrap.py Architecture

This is the core of everything. `bootstrap.py` is a self-contained, single-file installer. It embeds ALL template file contents as Python string literals in a `FILES = {}` dict, collects user inputs, creates a project folder, and launches Claude Code — with no external dependencies beyond Python 3.9+ stdlib.

### 3.1 File Header and Version

```python
#!/usr/bin/env python3
"""
bootstrap.py — ML Pipeline Template Bootstrap
Creates an ML project folder directly — no intermediate template folder.

Usage:
  python3 bootstrap.py          # interactive prompts → my-project_TIMESTAMP/

Via Docker:
  docker build -t ml-pipeline-template -f Dockerfile.bootstrap .
  docker run --rm -v $(pwd):/output ml-pipeline-template
"""

import os, sys, stat, shutil, subprocess, json
from pathlib import Path
from datetime import datetime, timezone

VERSION = "1.0.0"
```

### 3.2 Colour Codes

```python
G = "\033[0;32m"; C = "\033[0;36m"; B = "\033[1m"
Y = "\033[1;33m"; R = "\033[0;31m"; X = "\033[0m"
```

### 3.3 `collect_inputs()` — User Prompt Collection

Collects all user inputs interactively before any file creation occurs.

**Inputs collected (in order):**

| Field | Prompt | Default | Notes |
|---|---|---|---|
| `project_name` | "Project name" | `ml-project` | spaces replaced with `-` |
| `dataset_path` | "Dataset CSV path (press Enter to skip)" | `""` | resolved to absolute path; validated with `Path.is_file()` |
| `dataset_filename` | — | `""` | derived from `dataset_path` basename |
| `platform` | Deployment menu (1–8) | `"1"` | mapped to string key |
| `github_username` | "GitHub username" | auto-detected via `gh api user --jq .login` | empty = skip GitHub |
| `github_repo` | "GitHub repo name" | `project_name` | only asked if `github_username` provided |
| `github_visibility` | "Public / Private" | `"public"` | only asked if `github_username` provided |

**Platform mapping:**
```python
platform = {
    "1": "ask_later", "2": "render",  "3": "fly.io",
    "4": "railway",   "5": "aws",     "6": "gcp",
    "7": "azure",     "8": "none",
}.get(deploy_choice, "ask_later")
```

**GitHub auto-detection:**
```python
r = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                   capture_output=True, text=True, timeout=5)
if r.returncode == 0:
    gh_detected = r.stdout.strip()
```
If detected, show "GitHub account detected: `<username>`" and offer it as the default.

**Returns:** `dict` with keys: `project_name`, `dataset_path`, `dataset_filename`, `platform`, `github_username`, `github_repo`, `github_visibility`

### 3.4 `write_config(cfg, dest)` — Config File Writer

Writes `.ml_config.json` to the destination path (staging dir during bootstrap).

```python
def write_config(cfg, dest):
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    u, r = cfg["github_username"], cfg["github_repo"]
    config = {
        "project_name":        cfg["project_name"],
        "dataset_filename":    cfg["dataset_filename"] or "<not provided yet>",
        "dataset_path":        f"data/{cfg['dataset_filename']}" if cfg["dataset_filename"] else "<not provided yet>",
        "target_column":       "auto-detect",
        "task_type":           "auto-detect",
        "deployment_platform": cfg["platform"],
        "github_username":     u,
        "github_repo":         r,
        "github_visibility":   cfg["github_visibility"],
        "github_url":          f"https://github.com/{u}/{r}" if u else "",
        "python_version":      py,
        "created_at":          datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "venv_path":           ".venv",
        "template_version":    VERSION,
    }
    (dest / ".ml_config.json").write_text(json.dumps(config, indent=2))
```

### 3.5 `check_prereqs()` — Prerequisite Installer

Checks and auto-installs three tools in order:

1. **Homebrew** (macOS) — checks `shutil.which("brew")`; installs via `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` if missing; then sets `/opt/homebrew/bin` in `PATH`
2. **Node.js / npm** — checks `shutil.which("npm")`; installs via `brew install node`
3. **Claude Code CLI** — checks `shutil.which("claude")`; installs via `npm install -g @anthropic-ai/claude-code`

Each check prints either `"✔ <tool>"` (green) or a warning + install attempt (yellow).

### 3.6 The `FILES = {}` Dict — Embedded Template Content

This is the heart of `bootstrap.py`. Every file that needs to appear in the created project is stored as a Python string value, keyed by its relative path within the project.

```python
FILES = {}
FILES["CLAUDE.md"] = '''...'''
FILES["src/CLAUDE.md"] = '''...'''
FILES["deploy/CLAUDE.md"] = '''...'''
FILES["deploy/cloud.md"] = '''...'''
FILES["deploy/cloud-render.md"] = '''...'''
FILES["deploy/cloud-platforms.md"] = '''...'''
FILES["docs/CLAUDE.md"] = '''...'''
FILES["docs/claude_structure.md"] = '''...'''
FILES["docs/how_to_run.md"] = '''...'''
FILES["tests/CLAUDE.md"] = '''...'''
FILES[".gitignore"] = '''...'''
FILES[".ml_config.json.example"] = '''...'''
FILES["requirements.txt"] = '''...'''
FILES["README.md"] = '''...'''
FILES[".claude/settings.local.json"] = '''...'''
FILES["start.sh"] = r'''...'''    # raw string — preserves ANSI codes and backslashes
FILES["init.py"] = r'''...'''     # raw string
FILES["data/.gitkeep"] = ""
FILES["models/.gitkeep"] = ""
FILES["plots/.gitkeep"] = ""
```

**Important:** `start.sh` and `init.py` ARE included in `FILES` so they are available inside the created template folder when the user did `python3 bootstrap.py`. However, they are SKIPPED when writing files to the project (see Section 3.7).

**Raw strings** (`r'''...'''`) are required for `start.sh` and `init.py` because they contain backslashes (escape sequences in bash/Python heredocs) that must not be interpreted by Python.

### 3.7 Main Execution Block — APFS-Safe Staging Pattern

The main block runs after all function and `FILES` definitions:

```python
# 1. Banner
print(banner)

# 2. Check/install prerequisites
check_prereqs()

# 3. Collect user inputs
cfg = collect_inputs()

# 4. Determine paths
timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
project_dir = Path(".").resolve() / f"{cfg['project_name']}_{timestamp}"
staging_dir = project_dir.parent / f".ml_staging_{project_dir.name}"
```

**APFS-safe staging pattern — WHY it exists:**

On macOS APFS, `/tmp` is on a separate APFS volume from your home directory. When you do `shutil.move(str(staging_dir), str(project_dir))` and staging is in `/tmp`, Python must perform a cross-volume copy (not a rename). This means:
- VS Code's file watcher sees the destination folder appear EMPTY
- Files are then added one by one over several seconds
- VS Code may open files before they exist, causing confusion

The fix: create the staging dir in the SAME parent directory as the final project dir. On the same APFS volume, `shutil.move` (which calls `os.rename` under the hood) is a single atomic directory rename. VS Code sees the folder appear exactly ONCE, fully populated.

```python
# staging_dir is a sibling of project_dir — SAME filesystem volume
staging_dir = project_dir.parent / f".ml_staging_{project_dir.name}"
```

Naming convention: prefix with `.ml_staging_` + full project folder name. This makes it hidden (leading dot) and uniquely identifiable.

```python
# 5. Guard: fail if project already exists
if project_dir.exists():
    print(f"Error: '{project_dir.name}' already exists. Choose a different name.")
    sys.exit(1)

# 6. Create staging dir
staging_dir.mkdir(parents=True, exist_ok=True)

# 7. Write FILES — skip setup scripts
SKIP_IN_PROJECT = {"start.sh", "init.py"}
for rel_path, content in FILES.items():
    if rel_path in SKIP_IN_PROJECT:
        continue
    full = staging_dir / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")

# 8. Copy dataset if provided
if cfg["dataset_path"] and Path(cfg["dataset_path"]).is_file():
    (staging_dir / "data").mkdir(exist_ok=True)
    shutil.copy2(cfg["dataset_path"], staging_dir / "data" / cfg["dataset_filename"])

# 9. Write .ml_config.json
write_config(cfg, staging_dir)

# 10. Create .venv inside staging (invisible to VS Code)
subprocess.run([sys.executable, "-m", "venv", str(staging_dir / ".venv")], check=True)

# 11. Install dependencies
_pip = str(staging_dir / ".venv" / "bin" / "pip")
subprocess.run([_pip, "install", "--upgrade", "pip", "-q"], check=True)
subprocess.run([_pip, "install", "-r", str(staging_dir / "requirements.txt"), "-q"], check=True)

# 12. Atomic move — VS Code sees project appear ONCE, fully complete
print(f"Creating project at: {project_dir}")    # ONLY print here, not during staging
shutil.move(str(staging_dir), str(project_dir))

# 13. Fix .venv shebangs after path changed from staging to final
try:
    subprocess.run([sys.executable, "-m", "venv", "--upgrade",
                    str(project_dir / ".venv")],
                   check=True, capture_output=True)
except Exception:
    try:
        subprocess.run([str(project_dir / ".venv" / "bin" / "python"),
                        "-m", "pip", "install", "pip", "-q"],
                       check=False, capture_output=True)
    except Exception:
        pass

# 14. Launch Claude Code
os.chdir(project_dir)
if shutil.which("claude"):
    subprocess.run(["claude", "."])
else:
    print("Claude Code CLI not found. Install: npm install -g @anthropic-ai/claude-code")
    print(f"Then run: cd {project_dir} && source .venv/bin/activate && claude .")
```

**Why fix shebangs after the move?**

Python venvs embed absolute paths in their scripts (e.g., the shebang line in `.venv/bin/pip` points to the Python interpreter path). After `shutil.move`, the venv's internal paths still reference the old staging directory name. Running `python3 -m venv --upgrade <venv_path>` rewrites all the activation scripts and wrapper shebang lines to use the correct final path. This is mandatory for `pip`, `activate`, and other venv scripts to work.

### 3.8 Dockerfile.bootstrap

Used for users who want to create the template folder via Docker without installing Python locally.

```dockerfile
FROM python:3.11-slim

LABEL org.opencontainers.image.title="ML Pipeline Template"
LABEL org.opencontainers.image.description="Bootstraps an end-to-end ML template folder — no git clone required"
LABEL org.opencontainers.image.version="1.0.0"

COPY bootstrap.py /bootstrap.py
RUN chmod +x /bootstrap.py

WORKDIR /output
VOLUME ["/output"]

ENTRYPOINT ["python3", "/bootstrap.py"]
CMD ["ml-pipeline-template"]
```

**Usage:**
```bash
docker build -t ml-pipeline-template -f Dockerfile.bootstrap .
docker run --rm -v $(pwd):/output ml-pipeline-template
```

The container runs `bootstrap.py` in non-interactive mode (no prompts), writing files to `/output` which is mounted from the host. The default argument `ml-pipeline-template` sets the project folder name.

---

## 4. start.sh Architecture

`start.sh` is the bash entry point for users who cloned the template repo. It runs FROM INSIDE the template folder and creates the new project as a SIBLING directory.

### 4.1 Key Structural Properties

- Uses `set -e` (exit on error) with `set +e` relaxed during optional installs
- Same prerequisite checks as `bootstrap.py`: Homebrew, Node.js, Claude Code CLI
- Shows a 3-option entry mode menu first: Shell / Python CLI / Claude Code
- If option 2 is chosen: `exec python3 "$(dirname "$0")/init.py"` (hand off completely)
- Options 1 and 3 both proceed through the same shell prompts (1 = shell only, 3 = shell + claude launch)

### 4.2 Path Resolution

```bash
TEMPLATE_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="$(dirname "$TEMPLATE_DIR")/${PROJECT_NAME}_${TIMESTAMP}"
```

This places the project as a sibling of the template folder, not inside it.

### 4.3 APFS-Safe Staging in Bash

```bash
STAGING_DIR="$(dirname "$PROJECT_DIR")/.ml_staging_${PROJECT_NAME}_${TIMESTAMP}"
STAGING_DIR_SET=true

cleanup_staging() {
    if [ "${STAGING_DIR_SET:-false}" = "true" ] && [ -d "$STAGING_DIR" ]; then
        rm -rf "$STAGING_DIR" 2>/dev/null
    fi
}
trap cleanup_staging EXIT

mkdir -p "$STAGING_DIR"
```

The `trap cleanup_staging EXIT` ensures the staging dir is always removed if the script fails or is interrupted before the `mv` completes.

### 4.4 File Copy via rsync

```bash
rsync -a \
    --exclude='.git/' \
    --exclude='data/*.csv' \
    --exclude='models/*.pkl' \
    --exclude='models/*.npy' \
    --exclude='plots/*.png' \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='.DS_Store' \
    --exclude='.ml_config.json' \
    --exclude='bootstrap.py' \
    --exclude='Dockerfile.bootstrap' \
    --exclude='start.sh' \
    --exclude='init.py' \
    "$TEMPLATE_DIR/" "$STAGING_DIR/"
```

**Critical:** `bootstrap.py`, `Dockerfile.bootstrap`, `start.sh`, and `init.py` MUST be in the exclude list. These are setup scripts that belong in the template source repo, not in created projects.

### 4.5 Config File (Bash heredoc)

```bash
cat > "$STAGING_DIR/.ml_config.json" << CONFIGEOF
{
  "project_name": "${PROJECT_NAME}",
  "dataset_filename": "${DATASET_FILENAME_SAFE}",
  "dataset_path": "data/${DATASET_FILENAME_SAFE}",
  "target_column": "auto-detect",
  "task_type": "auto-detect",
  "deployment_platform": "${PLATFORM}",
  "github_username": "${GH_USER}",
  "github_repo": "${GH_REPO:-$PROJECT_NAME}",
  "github_visibility": "${GH_VIS}",
  "github_url": "https://github.com/${GH_USER}/${GH_REPO:-$PROJECT_NAME}",
  "python_version": "${PY_VER}",
  "created_at": "${CREATED_AT}",
  "venv_path": ".venv",
  "template_version": "1.0.0"
}
CONFIGEOF
```

`PY_VER=$(python3 --version 2>&1 | awk '{print $2}')` and `CREATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")`

### 4.6 Venv, Deps, Atomic Move, Shebang Fix

```bash
# Create venv inside staging (invisible to VS Code)
python3 -m venv "$STAGING_DIR/.venv"

# Install deps
"$STAGING_DIR/.venv/bin/pip" install --upgrade pip -q
"$STAGING_DIR/.venv/bin/pip" install -r "$STAGING_DIR/requirements.txt" -q

# Atomic move — print "Creating project at:" ONLY here
echo "Creating project at: $PROJECT_DIR"
mv "$STAGING_DIR" "$PROJECT_DIR"
STAGING_DIR_SET=false  # disable cleanup trap

# Fix shebangs
python3 -m venv --upgrade "$PROJECT_DIR/.venv" 2>/dev/null || \
    "$PROJECT_DIR/.venv/bin/python" -m pip install pip -q 2>/dev/null || true
```

### 4.7 Claude Launch

```bash
cd "$PROJECT_DIR"
source ".venv/bin/activate"
if command -v claude &>/dev/null; then
    claude .
else
    echo "Claude Code CLI not found. Install: npm install -g @anthropic-ai/claude-code"
    echo "Then run: cd $PROJECT_DIR && source .venv/bin/activate && claude ."
fi
```

---

## 5. init.py Architecture

`init.py` is the Python-equivalent of `start.sh`. It is the entry point when the user selects option 2 from `start.sh`'s menu, or runs `python3 init.py` directly. It also handles mode 3 (Claude Code) — both modes 2 and 3 go through full project setup.

### 5.1 Imports and Constants

```python
#!/usr/bin/env python3
"""
init.py — ML Pipeline Template: Python CLI Setup
Usage: python3 init.py
Requires: Python 3.9+ stdlib only (runs before venv is active)
"""

import os, sys, json, shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone
```

Stdlib only — no third-party imports. This script must work before any venv exists.

### 5.2 EXCLUDE Set — What NOT to Copy

```python
EXCLUDE = {
    ".git", "__pycache__", ".venv", ".DS_Store",
    ".ml_config.json",
    # Setup scripts: stay in the template folder, never copied into projects.
    "bootstrap.py", "Dockerfile.bootstrap", "start.sh", "init.py",
}
EXCLUDE_EXTS = {".csv", ".pkl", ".npy", ".png", ".pyc"}
```

The comment explaining WHY setup scripts are excluded is important — it documents the design decision that prevents the duplication bug.

### 5.3 `_ignore()` Function for `shutil.copytree`

```python
def _ignore(src: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        full = Path(src) / name
        if name in EXCLUDE:
            ignored.add(name)
        elif full.suffix in EXCLUDE_EXTS:
            ignored.add(name)
    return ignored
```

### 5.4 Staging Dir Helper

```python
def _make_staging_dir(project_dir: Path) -> Path:
    """
    Return a staging path in the SAME parent directory as project_dir.

    /tmp is on a different APFS volume — shutil.move from /tmp is a cross-volume
    COPY (VS Code sees folder appear empty, then files added one by one).
    Same-parent staging means shutil.move is an atomic RENAME on the same volume
    → VS Code sees the project folder appear ONCE, fully complete.
    """
    staging = project_dir.parent / f".ml_staging_{project_dir.name}"
    staging.mkdir(parents=True, exist_ok=True)
    return staging
```

### 5.5 `create_project(cfg)` — Path Calculation

```python
def create_project(cfg: dict) -> tuple:
    """Return (project_dir, staging_dir)."""
    template_dir = Path(__file__).parent.resolve()
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir  = template_dir.parent / f"{cfg['project_name']}_{timestamp}"
    staging_dir  = _make_staging_dir(project_dir)
    return project_dir, staging_dir
```

`template_dir.parent` places the project as a sibling of the template folder, not inside it.

### 5.6 `move_to_final()` — Atomic Move + Shebang Fix

```python
def move_to_final(staging_dir: Path, project_dir: Path):
    """
    Atomic move: staging → project_dir (same filesystem → os.rename, not copy).
    VS Code sees the project appear ONCE — fully populated, .venv already inside.
    Then fix .venv script shebangs (path changed from staging dir to project_dir).
    """
    print(f"\n▶ Creating project at: {project_dir}")    # ONLY here, not during staging
    shutil.move(str(staging_dir), str(project_dir))
    # Fix shebang paths in .venv/bin/pip etc. after the directory was renamed
    venv = project_dir / ".venv"
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", "--upgrade", str(venv)],
            check=True, capture_output=True
        )
    except Exception:
        # Fallback: reinstall pip to fix shebang (fast, no package reinstall)
        python = str(venv / "bin" / "python")
        subprocess.run([python, "-m", "pip", "install", "pip", "-q"],
                       check=False, capture_output=True)
```

### 5.7 `__main__` Block — Execution Order

```python
if __name__ == "__main__":
    banner()
    choice = mode_select()

    if choice == "1":
        # Hand off to start.sh
        script = Path(__file__).parent / "start.sh"
        os.execv("/bin/bash", ["/bin/bash", str(script)])

    # choices "2" and "3" both go through full project setup + launch
    cfg                      = collect_inputs()
    project_dir, staging_dir = create_project(cfg)

    # All heavy work in hidden staging dir (invisible to VS Code)
    copy_template(Path(__file__).parent.resolve(), staging_dir)  # 1. template files
    copy_dataset(cfg, staging_dir)                                # 2. dataset
    write_config(cfg, staging_dir)                                # 3. config
    create_venv(staging_dir)                                      # 4. .venv
    install_deps(staging_dir)                                     # 5. pip install

    # One atomic move → VS Code sees project appear once, complete
    move_to_final(staging_dir, project_dir)

    show_summary(cfg, project_dir)
    maybe_open_claude(project_dir)
```

---

## 6. .ml_config.json — Required Keys

Every created project must have a `.ml_config.json` at its root with exactly these keys:

```json
{
  "project_name":        "my-ml-project",
  "dataset_filename":    "titanic.csv",
  "dataset_path":        "data/titanic.csv",
  "target_column":       "auto-detect",
  "task_type":           "auto-detect",
  "deployment_platform": "render",
  "github_username":     "your-github-username",
  "github_repo":         "my-ml-project",
  "github_visibility":   "public",
  "github_url":          "https://github.com/your-github-username/my-ml-project",
  "python_version":      "3.11.9",
  "created_at":          "2026-05-25T12:00:00Z",
  "venv_path":           ".venv",
  "template_version":    "1.0.0"
}
```

**Key notes:**
- `dataset_path` is always `data/<filename>` (relative, inside project), NOT the original user-supplied path
- `target_column` and `task_type` start as `"auto-detect"` — Claude updates them after EDA
- `github_url` is `""` (empty string) if `github_username` was not provided
- `created_at` is UTC ISO 8601 format
- All three setup scripts (`bootstrap.py`, `start.sh`, `init.py`) produce identical JSON structure

---

## 7. CLAUDE.md Agent System

### 7.1 Root CLAUDE.md — Always Loaded

The root `CLAUDE.md` is loaded by Claude Code automatically when it opens the project. It must be concise (target: under 65 lines). It contains:

1. **Role and Objective** — "expert Data Scientist and Autonomous AI Agent"
2. **Token Management** — sub-agent delegation rules, context isolation
3. **Sub-Agent Roster** — table of agents with trigger and local spec file path

   | Agent | Trigger | Local spec |
   |---|---|---|
   | EDA Agent | Step 2 — EDA | `@src/CLAUDE.md` |
   | Data Engineering Agent | Step 3 — Preprocessing | `@src/CLAUDE.md` |
   | Optimization Agent | Steps 4–6 — Training | `@src/CLAUDE.md` |
   | FastAPI Agent | API development | `@src/CLAUDE.md` |
   | Docker Agent | Step 12 — Docker | `@deploy/CLAUDE.md` |
   | Documentation Agent | Steps 8, docs | `@docs/CLAUDE.md` |
   | Testing Agent | After pipeline | `@tests/CLAUDE.md` |
   | Git & Deploy Agent | Steps 11–13 | `@deploy/CLAUDE.md` |
   | Cloud Deploy Agent | Step 14 — Cloud | `@deploy/CLAUDE.md` |

4. **Token Conservation Rules** — never paste raw CSV/logs, sub-agents return summaries only
5. **Operational Rules** — immediate execution, state tracking, `random_state=42`
6. **Project Scope** — reads from `.ml_config.json`; tech stack
7. **ML Process Checklist** — Steps 0–14 as checkboxes
8. **Initialization Instructions** — the 6-step startup sequence Claude follows

### 7.2 Initialization Flow (what Claude does on startup)

Claude must follow these steps in order when it opens a project:

1. **Check for `.ml_config.json`** — if found, read all keys; if not, ask user one question at a time (dataset path, target column, GitHub username, repo name, platform)
2. **Check for `.venv/`** — if missing, create it and install `requirements.txt`; for all subsequent Python commands use `.venv/bin/python`
3. **Auto-detect task type** — if target column has ≤ 20 unique values or dtype is object/bool → Classification; otherwise → Regression
4. **Scan workspace** — read first 5 rows and column names of the CSV
5. **Show confirmation summary** and wait for Y/Enter:
   ```
   Dataset   : data/titanic.csv
   Target    : Survived
   Task      : Classification
   Platform  : render
   GitHub    : https://github.com/username/repo
   
   Proceed with the pipeline? [Y/n]
   ```
6. **Launch EDA Agent** (Step 2) immediately after confirmation

### 7.3 src/CLAUDE.md — Data Pipeline Agents

Contains specs for: EDA Agent, Data Engineering Agent, Optimization Agent, FastAPI Agent, plus instructions for Steps 8 (docs), 9 (requirements.txt), and 10 (workspace reorganization).

**EDA Agent** — saves all plots to `plots/`; returns bullet-point text summary only (no raw data, no code)

**Data Engineering Agent** — writes `src/preprocess.py` with:
- Drop non-feature columns (Id, Name, Ticket, Cabin, etc.)
- CoW-safe pandas: use `df.assign()` or `df.loc[:, col] =` not `df[col] =` after any drop/copy
- Derive features BEFORE dropping source columns
- Impute: median for numeric, most-frequent for categorical
- LabelEncoder for classification targets
- ColumnTransformer: StandardScaler (classification) or RobustScaler (regression)
- 80/20 stratified split (classification) or random (regression), `random_state=42`
- Save: `X_train_raw.pkl`, `X_test_raw.pkl`, `y_train.npy`, `y_test.npy`, `label_encoder.pkl`, `preprocessor.pkl`, `X_train.npy`, `X_test.npy`

**Optimization Agent** — runs GridSearchCV over candidate models, builds final sklearn Pipeline (`[('preprocessor', preprocessor), ('model', candidate)]`), saves `models/final_pipeline.pkl`

Candidate models (classification): LogisticRegression (saga), RandomForestClassifier, SVC (probability=True), GradientBoostingClassifier

Candidate models (regression): Ridge, RandomForestRegressor, GradientBoostingRegressor, SVR

**FastAPI Agent** — inspects the pipeline before writing `app.py`; replicates all pre-pipeline feature engineering; endpoints: `GET /health`, `POST /predict`, `POST /predict/batch`

### 7.4 deploy/CLAUDE.md — Deployment Agents

Contains specs for: Docker Agent, Git & Deploy Agent, Cloud Deploy Agent, plus Steps 11 (git init + GitHub push) and 12 (Dockerfile + containerization).

**deploy/cloud.md** — index file that `@`-imports the two cloud deployment files:
```
- Step 13 — Render: @deploy/cloud-render.md
- Step 14 — Generic: @deploy/cloud-platforms.md
```

**deploy/cloud-render.md** — Step 13: render.yaml, Render dashboard steps, verify deployment, create `docs/deployment_guide.md`

**deploy/cloud-platforms.md** — Step 14: platform comparison table, deploy commands for Fly.io, Railway, AWS App Runner, GCP Cloud Run, Azure Container Apps; universal smoke tests

### 7.5 tests/CLAUDE.md — Testing Agent

Writes `tests/test_pipeline.py` covering: artifact integrity, single-sample predictions, full test-set evaluation, per-class accuracy, consistency check, probability check.

Also documents the template test suite in `tests/template_tests/`:
- `run_tests.sh --fast` — 34 checks, ~30 seconds
- `run_tests.sh` — all checks including end-to-end (~10 min)
- `run_tests.sh --suite 03` — targeted suite

### 7.6 docs/CLAUDE.md — Documentation Agent

Writes: `docs/summary.md`, `docs/testing_guide.md`, `docs/test_results.md`, `docs/deployment_guide.md`, `docs/docker_guide.md`

---

## 8. Project vs Template Distinction

This distinction is the single most important design principle and the root cause of every duplication bug that has been fixed.

### The Rule

| Location | Stays in template repo? | Copied into project? |
|---|---|---|
| `bootstrap.py` | YES | NO |
| `Dockerfile.bootstrap` | YES | NO |
| `start.sh` | YES | NO |
| `init.py` | YES | NO |
| `CLAUDE.md` | YES | YES |
| `src/CLAUDE.md` | YES | YES |
| `deploy/*.md` | YES | YES |
| `docs/CLAUDE.md` | YES | YES |
| `tests/CLAUDE.md` | YES | YES |
| `requirements.txt` | YES | YES |
| `.gitignore` | YES | YES |
| `.claude/settings.local.json` | YES | YES |
| `README.md` | YES | YES |

### Why Setup Scripts Must Not Be in Projects

**bootstrap.py scenario:** If `bootstrap.py` is copied into a project folder and a user runs `python3 bootstrap.py` inside it, bootstrap.py creates a NEW project in the current directory — which is already the project folder. This creates a nested `project_name_TIMESTAMP/` inside the existing project. Result: duplication.

**start.sh/init.py scenario:** These scripts are designed to create a SIBLING project: `template_dir.parent / project_name_TIMESTAMP`. If they are inside a project folder (not the template folder), running them creates a sibling of the project folder rather than an independent workspace. Result: unexpected project proliferation.

**The fix:** Always include `bootstrap.py`, `Dockerfile.bootstrap`, `start.sh`, `init.py` in the SKIP/EXCLUDE set when writing files to a new project.

In `bootstrap.py`:
```python
SKIP_IN_PROJECT = {"start.sh", "init.py"}
# Note: bootstrap.py and Dockerfile.bootstrap are not in FILES dict at all,
# so they are never written to projects
```

In `start.sh` (rsync excludes):
```bash
--exclude='bootstrap.py'
--exclude='Dockerfile.bootstrap'
--exclude='start.sh'
--exclude='init.py'
```

In `init.py` (EXCLUDE set):
```python
EXCLUDE = {
    ".git", "__pycache__", ".venv", ".DS_Store", ".ml_config.json",
    "bootstrap.py", "Dockerfile.bootstrap", "start.sh", "init.py",
}
```

---

## 9. GitHub Setup Steps

### 9.1 Prerequisites

```bash
# Check GitHub CLI is installed
gh --version

# Install if missing (macOS)
brew install gh

# Check authentication
gh auth status

# Login if needed (opens browser OAuth)
gh auth login
```

### 9.2 Git Repository Initialization

```bash
cd ml-pipeline-template

git init
git add .
git commit -m "Initial commit: ML Pipeline Template v1.0.0"
```

### 9.3 Create GitHub Repo and Push

```bash
gh repo create ml-pipeline-template \
  --public \
  --description "Autonomous end-to-end ML pipeline template powered by Claude Code" \
  --source=. \
  --remote=origin \
  --push
```

### 9.4 Verify

```bash
gh repo view ml-pipeline-template --web
```

The raw bootstrap URL (needed in README.md) is:
```
https://raw.githubusercontent.com/<username>/ml-pipeline-template/main/bootstrap.py
```

### 9.5 README.md Bootstrap Curl URL

The README must contain the exact curl command users will run. Replace `<username>` with the actual GitHub username:

```bash
curl -O https://raw.githubusercontent.com/<username>/ml-pipeline-template/main/bootstrap.py
python3 bootstrap.py
```

This URL must be updated in both `README.md` and `docs/how_to_run.md` when the template is published.

---

## 10. requirements.txt — Pinned Versions

The `requirements.txt` in the template repo contains these pinned versions. They are the versions Claude installs in the generated `.venv` and are later pinned again after training (Step 9) with exact installed versions.

```
# ML Pipeline Template — auto-generated by the pipeline
# Generated: <date>
# Python <version> | random_state=42

# Core data manipulation
pandas==2.2.2
numpy==1.26.4

# Machine learning
scikit-learn==1.8.0
joblib==1.5.3

# Visualisation
matplotlib==3.10.9
seaborn==0.13.2

# API
fastapi==0.136.3
uvicorn==0.41.0
```

**Why pinned?** Reproducibility. The ML pipeline must produce identical results across environments. Unpinned versions risk API changes (especially sklearn) that silently alter model behavior or break preprocessing.

---

## 11. .claude/settings.local.json

Pre-authorized bash commands eliminate permission prompts during the Claude Code ML pipeline run. The file lives at `.claude/settings.local.json` inside the created project (copied from the template).

```json
{
  "permissions": {
    "allow": [
      "Bash(.venv/bin/pip install *)",
      "Bash(.venv/bin/pip install --upgrade *)",
      "Bash(.venv/bin/pip show *)",
      "Bash(.venv/bin/pip list *)",
      "Bash(.venv/bin/python *)",
      "Bash(.venv/bin/uvicorn *)",
      "Bash(python3 *)",
      "Bash(pip3 install *)",
      "Bash(pip install *)",
      "Bash(pkill -f uvicorn*)",
      "Bash(curl *)",
      "Bash(git init)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git push *)",
      "Bash(git remote *)",
      "Bash(git status)",
      "Bash(git log *)",
      "Bash(git branch *)",
      "Bash(gh repo create *)",
      "Bash(gh auth status)",
      "Bash(gh api *)",
      "Bash(docker build *)",
      "Bash(docker run *)",
      "Bash(docker stop *)",
      "Bash(docker rm *)",
      "Bash(docker images *)",
      "Bash(docker ps *)",
      "Bash(mkdir -p *)",
      "Bash(mv *)",
      "Bash(cp *)",
      "Bash(rm -rf __pycache__)",
      "Bash(find . -name __pycache__ *)",
      "Bash(find . -name *.pyc *)",
      "Bash(chmod +x *)"
    ]
  }
}
```

---

## 12. Common Pitfalls to Avoid

### Pitfall 1: Setup Scripts Copied into Projects

**Symptom:** Running `start.sh` inside a project creates an unexpected sibling project; running `bootstrap.py` inside a project creates a nested folder.

**Fix:** Always include `bootstrap.py`, `Dockerfile.bootstrap`, `start.sh`, `init.py` in the exclude/skip set when copying template files to a new project. This must be enforced in all three entry points independently (bootstrap.py's `SKIP_IN_PROJECT`, start.sh's rsync `--exclude` flags, init.py's `EXCLUDE` set).

### Pitfall 2: Using /tmp for Staging on macOS

**Symptom:** VS Code sees the project folder appear empty, then watches files populate one by one over several seconds. File watchers trigger on incomplete state.

**Root cause:** `/tmp` is on a separate APFS volume from `~`. `shutil.move()` across volumes is a copy operation, not a rename. The destination folder appears immediately (empty) and files are copied one by one.

**Fix:** Always create the staging directory in the SAME parent directory as the final project: `project_dir.parent / f".ml_staging_{project_dir.name}"`. Same-volume `shutil.move()` is an atomic rename — the folder appears exactly once, fully populated.

### Pitfall 3: Printing "Creating project at:" During Staging

**Symptom:** User sees the project path printed, looks in Finder/terminal, sees nothing yet (or sees the hidden `.ml_staging_*` dir). Confusing UX.

**Fix:** Print "Creating project at: `<path>`" ONLY at the moment of the `mv`/`shutil.move()` call, not before. The staging dir name starts with `.` so it is hidden by default.

### Pitfall 4: Relying on st_birthtime to Find Created Projects

**Symptom:** Code that tries to find the most recently created project folder using `os.stat(path).st_birthtime` fails or returns wrong results on APFS after a move operation (birth time reflects staging creation, not final move time).

**Fix:** Use the timestamp embedded in the folder name (`project_name_YYYYMMDD_HHMMSS`). The timestamp is set at `datetime.now().strftime("%Y%m%d_%H%M%S")` before staging begins, so it is always accurate and human-readable.

### Pitfall 5: Not Fixing Shebangs After venv Move

**Symptom:** After the atomic move from staging to final path, running `.venv/bin/pip` or `source .venv/bin/activate` fails because the embedded absolute paths point to the old staging directory (which no longer exists).

**Fix:** Always run `python3 -m venv --upgrade <venv_path>` immediately after `shutil.move()`. If that fails (e.g., permissions), fall back to `python -m pip install pip -q` inside the venv. This rewrites all activation scripts and wrapper shebang lines to the new path.

### Pitfall 6: Forgetting to Update the Bootstrap URL in README

**Symptom:** Users copy the curl command from README.md and get a 404 because the URL still contains a placeholder username.

**Fix:** After pushing to GitHub, update the curl URL in both `README.md` and `docs/how_to_run.md` with the actual GitHub username. The URL pattern is:
```
https://raw.githubusercontent.com/<username>/ml-pipeline-template/main/bootstrap.py
```

### Pitfall 7: Missing .gitkeep Files

**Symptom:** `data/`, `models/`, and `plots/` directories are missing in projects created via bootstrap (they are empty at template creation time and git doesn't track empty dirs).

**Fix:** Include `FILES["data/.gitkeep"] = ""`, `FILES["models/.gitkeep"] = ""`, `FILES["plots/.gitkeep"] = ""` in the `FILES` dict. These zero-byte files ensure the directories exist in the project and in git.

### Pitfall 8: pandas Copy-on-Write Warnings

**Symptom:** `FutureWarning: ChainedAssignmentError` in preprocessing code with pandas 2.x.

**Fix:** In `src/preprocess.py`, always use CoW-safe assignment:
- Correct: `df = df.assign(col=value)` or `df.loc[:, col] = value`
- Incorrect: `df[col] = value` (after any slice or copy operation)
- Derive new columns BEFORE dropping source columns

### Pitfall 9: SVC Without probability=True

**Symptom:** `predict_proba` fails on SVC model in the FastAPI `app.py` because SVC does not support probability output by default.

**Fix:** Always instantiate SVC as `SVC(probability=True, random_state=42)` in the Optimization Agent's candidate list.

### Pitfall 10: Fitting preprocessor on Full Dataset Instead of Train Split

**Symptom:** Data leakage — test set statistics influence the preprocessing pipeline, leading to optimistic evaluation metrics.

**Fix:** Fit the ColumnTransformer preprocessor ONLY on `X_train_raw`. Save it as `models/preprocessor.pkl` after fitting on training data only. The Optimization Agent then loads this pre-fitted preprocessor and includes it as the first step of the sklearn Pipeline.

---

---

## 13. Auto Pipeline Option (No Claude Subscription Required)

### Overview

Not every user has a Claude Code subscription. `auto_pipeline.py` provides a fully automated ML pipeline using pure sklearn — no AI required. It is embedded in the `FILES` dict inside `bootstrap.py` so it is automatically written into every new project.

### Launch Menu (appears at end of bootstrap.py)

After the project is created, bootstrap.py shows a 3-option menu:

```
How would you like to run the pipeline?
  1) Claude Code   — AI-driven, fully automated (recommended)
  2) Auto Pipeline — no Claude subscription needed (pure sklearn)
  3) Manual        — I'll run it myself later
Enter choice (default: 1):
```

- **Option 1** — launches `claude .` in the project directory (requires Claude Code CLI)
- **Option 2** — runs `.venv/bin/python auto_pipeline.py` immediately
- **Option 3** — prints instructions and exits; user runs manually later

### auto_pipeline.py Architecture

**File location in project:** `auto_pipeline.py` (project root)
**Embedded in bootstrap:** `FILES["auto_pipeline.py"] = r'''...'''`
**Setup scripts excluded from projects:** `start.sh`, `init.py` — but NOT `auto_pipeline.py` (it belongs in every project)

**Critical startup line:**
```python
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)   # ensures all relative paths resolve from project root
```
This must be the first thing after path setup — without it, relative paths like `models/final_pipeline.pkl` fail if the script is called from a different working directory.

**Execution steps (in order):**

| Step | What it does | Output |
|---|---|---|
| 0 | Resolve ROOT, chdir, create dirs (data/, models/, plots/, docs/) | — |
| 1 | Load `.ml_config.json`; if missing, prompt for dataset path + target column | config dict |
| 2 | Find CSV: try dataset_path from config → scan data/ for any .csv → exit with clear error if none found | csv_path |
| 3 | Import heavy deps (numpy, pandas, matplotlib, sklearn, joblib) after path check | — |
| 4 | EDA: print shape/dtypes/missing/class balance; save `plots/eda_correlation.png` + `plots/eda_target.png` | 2 PNG files |
| 5 | Auto-detect task type: ≤20 unique values or object/bool target → classification; else regression | task_type |
| 6 | Preprocessing: drop columns >50% missing; numeric→SimpleImputer(median)+StandardScaler/RobustScaler; categorical→SimpleImputer(most_frequent)+OneHotEncoder; LabelEncoder for target (classification) | ColumnTransformer |
| 7 | 80/20 stratified split (classification) or random split (regression), random_state=42 | X_train, X_test, y_train, y_test |
| 8 | GridSearchCV(cv=3, n_jobs=-1) over 3 candidates per task type | best model + params |
| 9 | Refit best pipeline on full train set; evaluate on test set | metrics |
| 10 | Save `models/final_pipeline.pkl` + `models/label_encoder.pkl` (classification) | .pkl files |
| 11 | Write `docs/auto_summary.md` with dataset info, model results, metrics, artifact paths | .md file |
| 12 | Print coloured summary banner to terminal | — |

**Candidate models:**

Classification:
- `LogisticRegression(solver='saga', random_state=42)` — grid: `C=[0.1, 1, 10]`
- `RandomForestClassifier(random_state=42)` — grid: `n_estimators=[100,200], max_depth=[None,5]`
- `GradientBoostingClassifier(random_state=42)` — grid: `n_estimators=[100,200], learning_rate=[0.05,0.1]`

Regression:
- `Ridge()` — grid: `alpha=[0.1, 1, 10]`
- `RandomForestRegressor(random_state=42)` — grid: `n_estimators=[100,200], max_depth=[None,5]`
- `GradientBoostingRegressor(random_state=42)` — grid: `n_estimators=[100,200], learning_rate=[0.05,0.1]`

**Artifacts produced:**

| File | Description |
|---|---|
| `models/final_pipeline.pkl` | Full sklearn Pipeline (ColumnTransformer + best model) |
| `models/label_encoder.pkl` | Fitted LabelEncoder (classification only) |
| `plots/eda_correlation.png` | Feature correlation heatmap |
| `plots/eda_target.png` | Target variable distribution |
| `docs/auto_summary.md` | Full markdown report with metrics and reproducibility snippet |

**Error handling:**
- If no CSV found: prints exact path to copy dataset into + re-run command, exits cleanly
- If a model fails GridSearchCV: skips it, continues with remaining candidates
- If fewer than 1 model succeeds: exits with clear error

### Key Implementation Notes for AI Agent

1. **Embed in FILES dict** — `FILES["auto_pipeline.py"]` must use a raw string `r'''...'''` to preserve backslashes
2. **Do NOT add to SKIP_IN_PROJECT** — unlike `start.sh`/`init.py`, `auto_pipeline.py` belongs in every project
3. **os.chdir(ROOT) is mandatory** — bootstrap calls `subprocess.run([python, "auto_pipeline.py"])` after `os.chdir(project_dir)`, but defensive chdir inside the script is required for direct invocation
4. **DATA_DIR must be defined** — `DATA_DIR = ROOT / "data"` used for auto-discovery glob
5. **Launch menu replaces direct claude launch** — the old `subprocess.run(["claude", "."])` becomes the 3-option menu at the end of bootstrap.py's main block

### Manual Usage (Option 3 or later)

```bash
cd my-project_20260525_143000
source .venv/bin/activate
python auto_pipeline.py         # run auto pipeline
# or
claude .                        # run Claude Code pipeline
```

### Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Missing `os.chdir(ROOT)` | `FileNotFoundError: models/final_pipeline.pkl` when called from wrong dir | Add `os.chdir(ROOT)` after ROOT is defined |
| `auto_pipeline.py` in SKIP_IN_PROJECT | File not written to project | Remove from SKIP set — it belongs in projects |
| No dataset in data/ | Script exits with confusing error | Clear message: "Copy your dataset into: {DATA_DIR}/" |
| Embedding with regular string | Backslash errors in ANSI codes | Use `r'''...'''` raw string in FILES dict |

---

*End of bootstrap_template_spec.md*
