# 🤖 ML Pipeline Template

> An autonomous, end-to-end machine learning template powered by Claude Code.
> Bring your CSV — the AI builds the pipeline, API, Docker image, and deploys it.

---

## What This Template Does

- 🔍 **Auto-detects** task type (classification vs regression) from your data
- 🧹 **Preprocesses** data: missing values, encoding, scaling
- 🏆 **Trains & tunes** models with GridSearchCV (multiple candidates)
- 📊 **Evaluates** with classification report / RMSE + R²
- 🌐 **Wraps** the model in a FastAPI REST API (`/predict`, `/predict/batch`)
- 🐳 **Containerises** with a multi-stage Docker image
- 🚀 **Deploys** to your chosen cloud platform
- 📄 **Documents** everything in `docs/`

---

## Prerequisites

| Tool | Install |
|---|---|
| Python 3.9+ | [python.org](https://python.org) |
| Git | `brew install git` |
| GitHub CLI | `brew install gh` |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop) |
| Claude Code CLI | `npm install -g @anthropic/claude-code` |

---

## Step 1 — Get the Template

Choose any one method:

### 🔥 Bootstrap (no git, no clone required)
```bash
# Download the single installer script and run it
curl -O https://raw.githubusercontent.com/ramleo/ml-pipeline-template/main/bootstrap.py
python3 bootstrap.py
cd ml-pipeline-template
```

### 🐳 Via Docker (nothing to install except Docker)
```bash
docker build -t ml-pipeline-template -f Dockerfile.bootstrap .
docker run --rm -v $(pwd):/output ml-pipeline-template
cd ml-pipeline-template
```

### 📦 Git Clone
```bash
git clone https://github.com/ramleo/ml-pipeline-template
cd ml-pipeline-template
```

---

## Step 2 — Run It (3 options)

### Option A — Shell Script (guided terminal prompts)
```bash
chmod +x start.sh
./start.sh
# Choose option 1 at the menu
```

### Option B — Python CLI (richer prompts)
```bash
python3 init.py
# Choose option 2 at the menu
```

### Option C — Claude Code Direct (AI-driven, recommended)
```bash
claude .
# Claude reads CLAUDE.md and asks everything automatically
```

> All three options create a **new project folder** (sibling to this template), set up a Python venv, copy template files, and launch the pipeline.

---

## What Gets Created

```
my-project_20260524_143000/
├── .venv/                  ← isolated Python environment
├── .ml_config.json         ← your choices (dataset, platform, etc.)
├── data/                   ← your CSV goes here
├── models/                 ← trained pipeline artifacts (.pkl)
├── plots/                  ← EDA charts (.png)
├── src/preprocess.py       ← generated preprocessing script
├── tests/test_pipeline.py  ← generated test suite
├── docs/                   ← summary, guides, test results
├── app.py                  ← FastAPI app
├── Dockerfile              ← multi-stage build
├── requirements.txt        ← pinned dependencies
└── render.yaml / fly.toml  ← deployment config
```

---

## Supported Deployment Platforms

| Platform | Free Tier | Config File | CLI |
|---|---|---|---|
| Render | ✅ | `render.yaml` | — |
| Fly.io | ✅ | `fly.toml` | `flyctl` |
| Railway | ✅ | `railway.toml` | `railway` |
| AWS App Runner | ✅ (free tier) | `apprunner.yaml` | `aws` |
| GCP Cloud Run | ✅ (free tier) | — | `gcloud` |
| Azure Container Apps | ✅ (free tier) | — | `az` |

---

## ML Tasks Supported

| Task | Target Column | Metrics |
|---|---|---|
| Classification | Categorical / ≤ 20 unique values | Accuracy, F1, Classification Report |
| Regression | Numeric / > 20 unique values | RMSE, MAE, R² |

Task type is **auto-detected** from your target column — no config needed.

---

## Template File Reference

| File | Purpose |
|---|---|
| `CLAUDE.md` | Root agent instructions (always loaded) |
| `src/CLAUDE.md` | EDA, preprocessing, training agent specs |
| `tests/CLAUDE.md` | Testing agent spec |
| `docs/CLAUDE.md` | Documentation agent spec |
| `deploy/CLAUDE.md` | Docker, Git, cloud deploy agent specs |
| `deploy/cloud-render.md` | Render deployment steps |
| `deploy/cloud-platforms.md` | AWS / GCP / Azure / Fly.io / Railway steps |
| `start.sh` | Bash entry point |
| `init.py` | Python CLI entry point |
| `bootstrap.py` | Single-file installer (no git required) |
| `Dockerfile.bootstrap` | Docker image for distributing the template |
| `.ml_config.json.example` | Reference config template |

---

## Customisation

Edit the local `CLAUDE.md` files in subdirectories to change agent behaviour:
- **Add candidate models** → `src/CLAUDE.md` (Optimization Agent section)
- **Change preprocessing** → `src/CLAUDE.md` (Data Engineering Agent section)
- **Add API endpoints** → `src/CLAUDE.md` (FastAPI Agent section)
- **Change deploy target** → `deploy/CLAUDE.md`

---

## License

MIT — free to use, modify, and distribute.
