# How to Run the ML Pipeline Template

---

## Prerequisites

Only **Python 3.9+** must be installed manually — `start.sh` and `bootstrap.py` auto-install everything else.

| Tool | How |
|---|---|
| Python 3.9+ | Manual — [python.org](https://python.org) |
| Homebrew | **Auto-installed** by `./start.sh` / `bootstrap.py` |
| Node.js | **Auto-installed** by `./start.sh` / `bootstrap.py` |
| Claude Code CLI | **Auto-installed** by `./start.sh` / `bootstrap.py` |
| GitHub CLI *(optional)* | `brew install gh` then `gh auth login` |
| Docker *(optional)* | [docker.com](https://docker.com) |

---

## Step 1 — Download the bootstrap script

```bash
curl -O https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/bootstrap.py
```

---

## Step 2 — Run it

```bash
python3 bootstrap.py
```

This creates `ml-pipeline-template/` in your current directory with all template files.

---

## Step 3 — Enter the template folder

```bash
cd ml-pipeline-template
```

---

## Step 4 — Start the wizard (pick one)

| Option | Command | Best for |
|---|---|---|
| **Claude Code** *(recommended)* | `claude .` | Fully AI-driven, hands-free |
| **Shell wizard** | `./start.sh` | Guided terminal prompts |
| **Python wizard** | `python3 init.py` | Richer prompts, same as shell |

---

## Step 5 — Answer the prompts

Whichever option you chose, you will be asked:

1. **Project name** — e.g. `house-price-predictor`
2. **Dataset CSV path** — full path to your `.csv` file (or skip to drop it in later)
3. **Deployment platform** — Render, Fly.io, Railway, AWS, GCP, Azure, or skip
4. **GitHub username** — auto-detected if you are logged into `gh`; or type it; or skip
5. **Repo visibility** — public or private

---

## Step 6 — Claude runs the pipeline

A new project folder is created one level up (e.g. `../house-price-predictor_20260524_143000/`).  
Claude then works through the 14-step checklist automatically:

| Step | Task |
|---|---|
| 0 | Creates Python virtual environment (`.venv`) |
| 1 | Scans workspace, finds your CSV |
| 2 | EDA — plots saved to `plots/` |
| 3 | Preprocessing — writes `src/preprocess.py` |
| 4–6 | Model training, tuning & evaluation |
| 7 | Saves final pipeline to `models/final_pipeline.pkl` |
| 8 | Summary report → `docs/summary.md` |
| 9 | Generates `requirements.txt` with pinned versions |
| 10 | Reorganises workspace into standard folder structure |
| 11 | Git init → first commit → GitHub repo created → push |
| 12 | Dockerfile written, image built & smoke-tested locally |
| 13 | Deploys to your chosen cloud platform |

---

## Folder layout after bootstrap

```
ml-pipeline-template/          ← the template (stays untouched between runs)
│
└── (after running ./start.sh or claude .)

house-price-predictor_20260524_143000/    ← your new isolated ML project
├── .venv/                  ← Python virtual environment
├── .ml_config.json         ← your choices (dataset, platform, GitHub)
├── data/                   ← your CSV file goes here
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

If you prefer not to run Python directly, use Docker to scaffold the template:

```bash
# Build the Docker image once
docker build -t ml-pipeline-template -f Dockerfile.bootstrap \
  https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/Dockerfile.bootstrap

# Run it — creates ml-pipeline-template/ in your current directory
docker run --rm -v $(pwd):/output ml-pipeline-template

# Then start normally
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

## Quick reference card

```bash
# 1. Get it
curl -O https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/bootstrap.py

# 2. Create the template folder
python3 bootstrap.py

# 3. Go in and launch
cd ml-pipeline-template
claude .
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python3: command not found` | Install Python 3.9+ from [python.org](https://python.org) |
| `claude: command not found` | Run `./start.sh` — it auto-installs Claude Code CLI, or manually: `npm install -g @anthropic/claude-code` |
| `gh: command not found` | Run `brew install gh` then `gh auth login` |
| `Permission denied: ./start.sh` | Run `chmod +x start.sh` first |
| Dataset not found | Copy your `.csv` into the project's `data/` folder manually, then tell Claude its name |
| `ml-pipeline-template/` already exists | Run `python3 bootstrap.py my-new-name` to use a different folder name |
