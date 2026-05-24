#!/usr/bin/env python3
"""
init.py — ML Pipeline Template: Python CLI Setup
Usage: python3 init.py
Requires: Python 3.9+ stdlib only (runs before venv is active)
"""

import os, sys, json, shutil, subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── Colours ────────────────────────────────────────────────────────
G = "\033[0;32m"; Y = "\033[1;33m"; C = "\033[0;36m"
B = "\033[1m";    R = "\033[0;31m"; X = "\033[0m"

PLATFORMS = {
    "1": "ask_later", "2": "render",  "3": "fly.io",
    "4": "railway",   "5": "aws",     "6": "gcp",
    "7": "azure",     "8": "none",
}

PLATFORM_LABELS = {
    "ask_later": "Ask me later",
    "render":    "Render (free tier)",
    "fly.io":    "Fly.io",
    "railway":   "Railway",
    "aws":       "AWS App Runner",
    "gcp":       "GCP Cloud Run",
    "azure":     "Azure Container Apps",
    "none":      "Skip (local / Docker only)",
}

def prompt(msg: str, default: str = "") -> str:
    suffix = f" (default: {default})" if default else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val or default

def menu(title: str, options: list[tuple[str, str]], default: str = "1") -> str:
    print(f"\n{B}{title}{X}")
    for key, label in options:
        print(f"  {key}) {label}")
    choice = input(f"Enter choice [{'/'.join(k for k,_ in options)}] (default: {default}): ").strip()
    return choice or default

def banner():
    print(f"""
{C}{B}╔══════════════════════════════════════════════════╗
║        🤖  ML Pipeline Template  v1.0.0          ║
║   End-to-End Machine Learning Automation         ║
╚══════════════════════════════════════════════════╝{X}
""")

def mode_select() -> str:
    choice = menu(
        "How would you like to run this template?",
        [
            ("1", "Shell script  — guided prompts here in the terminal"),
            ("2", "Python CLI    — richer prompts via init.py  ← you are here"),
            ("3", "Claude Code   — AI-driven, fully automated (recommended)"),
        ],
        default="3",
    )
    return choice

def collect_inputs() -> dict:
    print(f"\n{B}── Project Setup ──────────────────────────────────────{X}")

    project_name = prompt("Project name", "ml-project").replace(" ", "-")

    # Dataset
    dataset_path = ""
    dataset_filename = ""
    raw = prompt("Dataset CSV path (press Enter to provide manually later)", "")
    if raw:
        p = Path(raw).expanduser().resolve()
        if p.is_file():
            dataset_path = str(p)
            dataset_filename = p.name
            print(f"  {G}✔ Found: {dataset_filename}{X}")
        else:
            print(f"  {Y}⚠ File not found — you can copy it to data/ later.{X}")

    # Deployment
    deploy_choice = menu(
        "Deployment platform (applied at end of pipeline):",
        [
            ("1", "Ask me later"),
            ("2", "Render        (free tier, recommended)"),
            ("3", "Fly.io"),
            ("4", "Railway"),
            ("5", "AWS App Runner"),
            ("6", "GCP Cloud Run"),
            ("7", "Azure Container Apps"),
            ("8", "Skip (local / Docker only)"),
        ],
        default="1",
    )
    platform = PLATFORMS.get(deploy_choice, "ask_later")

    # GitHub username — auto-detect from gh CLI if available
    print(f"\n{B}GitHub setup:{X}")
    gh_detected = ""
    try:
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            gh_detected = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if gh_detected:
        print(f"  {G}✔ GitHub account detected: {gh_detected}{X}")
        gh_user = prompt(f"  GitHub username (press Enter to use '{gh_detected}')", gh_detected)
    else:
        gh_user = prompt("  GitHub username (press Enter to skip GitHub setup)", "")

    # Repo name — defaults to project name (no timestamp)
    gh_repo = ""
    gh_vis  = "skip"
    if gh_user:
        gh_repo = prompt(f"  GitHub repo name", project_name).replace(" ", "-")
        gh_choice = menu(
            "  GitHub repo visibility:",
            [("1", "Public"), ("2", "Private")],
            default="1",
        )
        gh_vis = "private" if gh_choice == "2" else "public"
    else:
        print(f"  {Y}⚠ No GitHub username provided — skipping GitHub setup.{X}")

    return {
        "project_name":      project_name,
        "dataset_path":      dataset_path,
        "dataset_filename":  dataset_filename,
        "platform":          platform,
        "github_username":   gh_user,
        "github_repo":       gh_repo or project_name,
        "github_visibility": gh_vis,
    }

def create_project(cfg: dict) -> Path:
    template_dir = Path(__file__).parent.resolve()
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir  = template_dir.parent / f"{cfg['project_name']}_{timestamp}"
    project_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{G}▶ Creating project at: {project_dir}{X}")
    return project_dir

def create_venv(project_dir: Path):
    print(f"{G}▶ Setting up Python environment...{X}")
    subprocess.run([sys.executable, "-m", "venv", str(project_dir / ".venv")], check=True)
    print(f"  {G}✔ Virtual environment created{X}")
    print(f"{G}▶ Installing dependencies (this may take a minute)...{X}")
    pip = str(project_dir / ".venv" / "bin" / "pip")
    subprocess.run([pip, "install", "--upgrade", "pip", "-q"], check=True)
    req = project_dir / "requirements.txt"
    if req.exists():
        subprocess.run([pip, "install", "-r", str(req), "-q"], check=True)
    print(f"  {G}✔ Dependencies installed{X}")

EXCLUDE = {
    ".git", "__pycache__", ".venv", ".DS_Store",
    ".ml_config.json", "start.sh", "init.py",
}
EXCLUDE_EXTS = {".csv", ".pkl", ".npy", ".png", ".pyc"}

def _ignore(src: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        full = Path(src) / name
        if name in EXCLUDE:
            ignored.add(name)
        elif full.suffix in EXCLUDE_EXTS:
            ignored.add(name)
    return ignored

def copy_template(template_dir: Path, project_dir: Path):
    print(f"{G}▶ Copying template files...{X}")
    shutil.copytree(str(template_dir), str(project_dir), ignore=_ignore, dirs_exist_ok=True)
    print(f"  {G}✔ Template files copied{X}")

def copy_dataset(cfg: dict, project_dir: Path):
    if cfg["dataset_path"] and Path(cfg["dataset_path"]).is_file():
        dest = project_dir / "data"
        dest.mkdir(exist_ok=True)
        shutil.copy2(cfg["dataset_path"], dest / cfg["dataset_filename"])
        print(f"  {G}✔ Dataset copied: {cfg['dataset_filename']}{X}")

def write_config(cfg: dict, project_dir: Path):
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    gh_user = cfg.get("github_username", "")
    gh_repo = cfg.get("github_repo", cfg["project_name"])
    config = {
        "project_name":      cfg["project_name"],
        "dataset_filename":  cfg["dataset_filename"] or "<not provided yet>",
        "dataset_path":      f"data/{cfg['dataset_filename']}" if cfg["dataset_filename"] else "<not provided yet>",
        "target_column":     "auto-detect",
        "task_type":         "auto-detect",
        "deployment_platform": cfg["platform"],
        "github_username":   gh_user,
        "github_repo":       gh_repo,
        "github_visibility": cfg["github_visibility"],
        "github_url":        f"https://github.com/{gh_user}/{gh_repo}" if gh_user else "",
        "python_version":    py_ver,
        "created_at":        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "venv_path":         ".venv",
        "template_version":  "1.0.0",
    }
    (project_dir / ".ml_config.json").write_text(json.dumps(config, indent=2))
    print(f"  {G}✔ .ml_config.json written{X}")

def show_summary(cfg: dict, project_dir: Path):
    fn   = cfg["dataset_filename"] or "<not provided yet>"
    plat = PLATFORM_LABELS.get(cfg["platform"], cfg["platform"])
    gh_user = cfg.get("github_username", "")
    gh_repo = cfg.get("github_repo", cfg["project_name"])
    gh_line = f"\n{C}{B}║{X}  🐙  GitHub : github.com/{gh_user}/{gh_repo}" if gh_user else ""
    print(f"""
{C}{B}╔══════════════════════════════════════════════════╗
║  ✅  Project ready!                              ║
╠══════════════════════════════════════════════════╣{X}
{C}{B}║{X}  📁  {project_dir}
{C}{B}║{X}  🐍  Venv   : .venv/
{C}{B}║{X}  📊  Data   : {fn}
{C}{B}║{X}  🚀  Deploy : {plat}{gh_line}
{C}{B}╠══════════════════════════════════════════════════╣{X}
{C}{B}║{X}  ✅  Launching Claude Code...
{C}{B}╚══════════════════════════════════════════════════╝{X}
""")

def maybe_open_claude(project_dir: Path):
    print(f"{G}▶ Launching Claude Code in your new project...{X}")
    os.chdir(project_dir)
    if shutil.which("claude"):
        subprocess.run(["claude", "."])
    else:
        print(f"{Y}Claude Code CLI not found. Install: npm install -g @anthropic-ai/claude-code{X}")
        print(f"Then run: {B}cd {project_dir} && source .venv/bin/activate && claude .{X}")


if __name__ == "__main__":
    banner()
    choice = mode_select()

    if choice == "1":
        script = Path(__file__).parent / "start.sh"
        os.execv("/bin/bash", ["/bin/bash", str(script)])

    # choices "2" and "3" both go through full project setup + launch
    cfg         = collect_inputs()
    project_dir = create_project(cfg)
    copy_template(Path(__file__).parent.resolve(), project_dir)
    copy_dataset(cfg, project_dir)
    write_config(cfg, project_dir)
    create_venv(project_dir)
    show_summary(cfg, project_dir)
    maybe_open_claude(project_dir)
