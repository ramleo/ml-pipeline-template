# How to Run the ML Pipeline Template

---

## Prerequisites

Only **Python 3.9+** must be installed manually — everything else is handled automatically.

| Tool | How |
|---|---|
| Python 3.9+ | Manual — [python.org](https://python.org) |
| Homebrew | **Auto-installed** by `./start.sh` or `bootstrap.py` |
| Node.js | **Auto-installed** by `./start.sh` or `bootstrap.py` |
| Claude Code CLI | **Auto-installed** by `./start.sh` or `bootstrap.py` |
| GitHub CLI *(optional)* | `brew install gh` then `gh auth login` |
| Docker *(optional)* | [docker.com](https://docker.com) |

---

## Step 1 — Check Python

```bash
python3 --version
```

If you get `command not found`, install Python 3.9+ from [python.org](https://python.org) before continuing.

---

## Step 2 — Download the bootstrap script

```bash
curl -O https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/bootstrap.py
```

This downloads a single installer file — no git, no GitHub account required.

---

## Step 3 — Run the bootstrap

```bash
python3 bootstrap.py
```

This will:
- Create a `ml-pipeline-template/` folder with all template files
- Auto-install **Homebrew**, **Node.js**, and **Claude Code CLI** if they're missing

---

## Step 4 — Enter the template folder

```bash
cd ml-pipeline-template
```

---

## Step 5 — Start the wizard

```bash
./start.sh
```

The script checks prerequisites (installs anything still missing), then shows a menu:

```
How would you like to run this template?
  1) Shell script  — guided prompts here in the terminal
  2) Python CLI    — richer prompts via init.py
  3) Claude Code   — AI-driven, fully automated (recommended)
```

Choose **3** (or press Enter — it is the default).

---

## Step 6 — Answer Claude's questions

Claude will ask for:

| Question | Example |
|---|---|
| Path to your CSV file | `/Users/yourname/Downloads/titanic.csv` |
| Target column | `Survived` (Claude can auto-detect this) |
| Deployment platform | Render, Fly.io, Railway, AWS, GCP, Azure, or skip |
| GitHub username | `your-github-username` (optional) |

### When to add your CSV file

**You do not need to move your CSV anywhere beforehand.** Just have it somewhere on your computer and know its full path.

When Claude asks `Please provide your dataset CSV path:`, type the full path to wherever the file already is — Claude copies it into the project's `data/` folder automatically.

| Situation | What to do |
|---|---|
| File is anywhere on your computer | Type its full path when Claude asks, e.g. `/Users/yourname/Downloads/mydata.csv` |
| File is not ready yet | Press Enter to skip — drop the CSV into the project's `data/` folder later and tell Claude the filename |

---

## Step 7 — Pipeline runs automatically

Claude works through the full pipeline checklist:

| Step | Task | Output |
|---|---|---|
| 0 | Create Python virtual environment | `.venv/` |
| 1 | Scan workspace, find CSV | — |
| 2 | EDA — profile data, plot charts | `plots/` |
| 3 | Preprocessing — clean & encode | `src/preprocess.py` |
| 4–6 | Train, tune & evaluate models | metrics report |
| 7 | Save final pipeline | `models/final_pipeline.pkl` |
| 8 | Write summary report | `docs/summary.md` |
| 9 | Pin dependencies | `requirements.txt` |
| 10 | Reorganise workspace | clean folder structure |
| 11 | Git init → GitHub repo → push | GitHub URL |
| 12 | Dockerfile → build → smoke-test | Docker image |
| 13 | Deploy to chosen cloud platform | live URL |

---

## Folder layout after the pipeline

```
your-project_20260524_143000/
├── .venv/                  ← Python virtual environment
├── .ml_config.json         ← your choices (dataset, platform, GitHub)
├── data/                   ← your CSV file
├── models/                 ← trained pipeline artifacts (.pkl)
├── plots/                  ← EDA charts (.png)
├── src/preprocess.py       ← auto-generated preprocessing script
├── tests/test_pipeline.py  ← auto-generated test suite
├── docs/                   ← summary, guides, test results
├── app.py                  ← FastAPI prediction API
├── Dockerfile              ← multi-stage container build
├── requirements.txt        ← pinned library versions
└── render.yaml / fly.toml  ← deployment config
```

> The template folder is **never modified**. Each run produces a fresh, isolated project.

---

## Alternative: get the template via Docker

If you prefer not to run Python directly:

```bash
docker build -t ml-pipeline-template -f Dockerfile.bootstrap \
  https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/Dockerfile.bootstrap

docker run --rm -v $(pwd):/output ml-pipeline-template

cd ml-pipeline-template
./start.sh
```

---

## Alternative: get the template via git clone

```bash
git clone https://github.com/ramleo/ml-pipeline-template
cd ml-pipeline-template
./start.sh
```

---

## Quick reference

```bash
python3 --version          # 1. confirm Python is installed
curl -O <bootstrap_url>    # 2. download installer
python3 bootstrap.py       # 3. create template + auto-install tools
cd ml-pipeline-template    # 4. enter folder
./start.sh                 # 5. launch — choose option 3
```

*(Replace `<bootstrap_url>` with `https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/bootstrap.py`)*

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` | Install Python 3.9+ from [python.org](https://python.org) |
| `claude: command not found` | Run `./start.sh` — it auto-installs, or manually: `npm install -g @anthropic-ai/claude-code` |
| `Permission denied: ./start.sh` | Run `chmod +x start.sh` first |
| Dataset not found | Copy your `.csv` into the project's `data/` folder, then tell Claude its name |
| `ml-pipeline-template/` already exists | Run `python3 bootstrap.py my-new-name` to use a different folder name |
| Homebrew install hangs | Accept the Xcode Command Line Tools prompt that appears |
