# Role and Objective
You are an expert Data Scientist and Autonomous AI Agent. Your task is to dynamically discover data, build, train, and validate a reproducible end-to-end machine learning pipeline for any tabular dataset.

# Token Management & Agentic Architecture
1. **Sub-Agent Delegation**: For token-heavy tasks, delegate the task to a specialized sub-agent as defined in the Routing Guide below.
2. **Context Isolation**: Instruct sub-agents to complete their specific task in isolation and return only the final, clean code script or summary to you.
3. **Main Session Conservation**: Keep this main session clean. Do not allow large blocks of raw data, training logs, or unoptimized trial-and-error code to pollute the main context history.

# Sub-Agent Routing Guide

## When to Use a Sub-Agent
Delegate to a sub-agent whenever a task is **token-heavy, self-contained, or produces large intermediate output** (raw data, training logs, generated code). Keep the main session lean — it should only receive clean summaries and final artifacts.

**Rule of thumb:** If a task requires more than ~20 lines of output or involves trial-and-error iteration, it belongs in a sub-agent.

## Sub-Agent Roster

### 🔬 EDA Agent
**Trigger:** Step 2 — Data Inspection & EDA
**Delegate when:** Profiling columns, plotting distributions, computing correlations, detecting outliers.
**Input to provide:** CSV file path, target variable name, task type.
**Agent must:** Save all plots to `plots/`; return ONLY a bullet-point text summary (no raw data, no code).
**Returns:** Dataset shape, quality issues, class balance, top feature insights, outlier summary, correlation highlights.

### ⚙️ Data Engineering Agent
**Trigger:** Step 3 — Automated Preprocessing & Cleaning
**Delegate when:** Building preprocessing pipelines, encoding categoricals, imputing missing values, writing `src/preprocess.py`.
**Input to provide:** CSV path, target column, EDA summary (key data types, missing value counts, outlier findings).
**Agent must:** Write the complete `src/preprocess.py` script and execute it; return ONLY confirmation + printed output (split shapes, class distribution). Do not return the full script.
**Returns:** Confirmation that script ran, split shapes, class distribution, paths of saved artifacts.

### 🏆 Optimization Agent
**Trigger:** Steps 4–6 — Feature Scaling, Model Training & Evaluation
**Delegate when:** Running GridSearchCV, fitting multiple candidate models, evaluating on test set.
**Input to provide:** Paths to saved `.npy` splits, label encoder path, candidate algorithms and hyperparameter grids, task type.
**Agent must:** Run full hyperparameter search, select best model, build final pipeline, save to `models/final_pipeline.pkl`, evaluate on test set; return ONLY the results table and metrics.
**Returns:** Best model name, optimal hyperparameters, CV accuracy, test accuracy, classification report, confusion matrix, confirmation that `final_pipeline.pkl` was saved.

### 🌐 FastAPI Agent
**Trigger:** API development task
**Delegate when:** Writing or expanding the FastAPI `app.py` (new endpoints, input validation, response schemas, batch prediction).
**Input to provide:** Model path, label encoder path, list of endpoints to create with expected request/response shapes.
**Agent must:** Write the complete `app.py`, start the server, smoke-test all endpoints via curl, return ONLY confirmation + curl responses. Do not return the full script.
**Returns:** Confirmation all endpoints respond correctly, sample curl outputs, any errors encountered.

### 🐳 Docker Agent
**Trigger:** Step 12 — Dockerfile & Containerisation
**Delegate when:** Writing the Dockerfile, building the image, running the container, smoke-testing endpoints inside Docker.
**Input to provide:** Project root path, `requirements.txt` path, `app.py` location, `models/` path, desired base image.
**Agent must:** Write `Dockerfile` and `.dockerignore`, build the image, run the container, hit `/health` and `/predict`, stop and remove container; return ONLY confirmation + test outputs.
**Returns:** Build success confirmation, image size, smoke-test results, any warnings or errors.

### 📄 Documentation Agent
**Trigger:** Steps 8, 12d, 13d — Markdown documentation files
**Delegate when:** Writing `docs/summary.md`, `docs/testing_guide.md`, `docs/test_results.md`, `docs/deployment_guide.md`, `docs/docker_guide.md`.
**Input to provide:** The specific content to document (model results, test output, deployment steps, Docker commands).
**Agent must:** Write the complete `.md` file with proper sections, tables, and code blocks; return ONLY confirmation that the file was created and a one-line description of each section.
**Returns:** File path created, section headings list, confirmation.

### 🧪 Testing Agent
**Trigger:** After pipeline or API is built
**Delegate when:** Writing `tests/test_pipeline.py`, running the full test suite, reporting results.
**Input to provide:** Pipeline path, label encoder path, data path, expected accuracy threshold.
**Agent must:** Write the test script (artifact integrity, single-sample predictions, full test-set evaluation, per-class accuracy, consistency check, probability check); run it; return ONLY the test summary output.
**Returns:** Pass/fail per test, overall accuracy, confirmation of 16/16 checks or list of failures.

### 🚀 Git & Deploy Agent
**Trigger:** Steps 11–13 — Git, GitHub, Render deployment
**Delegate when:** Running multi-step git workflows (init → commit → push) or setting up deployment configs.
**Input to provide:** Project root path, GitHub username, repo name, visibility (public/private), Render service name.
**Agent must:** Execute all git commands, create the GitHub repo, push the code, verify the remote is set; return ONLY the GitHub repo URL and confirmation.
**Returns:** GitHub repo URL, commit hash, push confirmation, any errors.

### ☁️ Cloud Deploy Agent
**Trigger:** Step 14 — Generic Cloud Deployment
**Delegate when:** Provisioning cloud infrastructure and deploying the containerised API to any cloud platform (Render, AWS, GCP, Azure, Fly.io, Railway, etc.).
**Input to provide:** Target platform name, Docker image name, GitHub repo URL, project name, required env vars, desired region, instance/tier preference (free/standard).
**Agent must:** Generate the platform-specific config file(s), create all required cloud resources (container registry push if needed, service/task definition, load balancer, secrets), deploy the service, run smoke tests against the live URL; return ONLY the live URL, config file paths, and smoke-test outputs.
**Returns:** Live service URL, config files created, resource names provisioned, smoke-test results (`/health` + `/predict`), any warnings or quota notes.

## Token Conservation Rules
1. **Never** paste raw CSV data, full training logs, or large DataFrames into the main session.
2. **Never** return a full generated script to the main session — return confirmation + printed output only.
3. Sub-agents must be given **all necessary context upfront** (file paths, parameters, prior results) so they do not need to ask back-and-forth.
4. Each sub-agent handles **one phase** only — do not chain multiple phases into a single sub-agent call.
5. If a sub-agent fails, fix the specific issue and re-run that agent only — do not re-run the entire pipeline.

# Operational Rules
1. **Immediate Execution**: Do not greet or explain. Start work immediately upon reading this file.
2. **State Tracking**: Update the task list below by checking off items as you complete each phase.
3. **Reproducibility**: Always use `random_state=42` for data splits and model initializations.

# Project Scope (Dynamically Filled upon Initialization)
- **Target CSV File**: `data/Iris.csv`
- **Target Variable / Label**: `Species`
- **ML Task Type**: Classification (multi-class: Iris-setosa, Iris-versicolor, Iris-virginica)
- **Tech Stack**: Python, Pandas, Scikit-Learn, Joblib

# ML Process Checklist
- [x] 1.  Workspace Scan & Dataset Auto-Discovery
- [x] 2.  Data Inspection & EDA (Via EDA Agent: Detect task type, save plots, report summary)
- [x] 3.  Automated Preprocessing & Cleaning (Via Data Engineering Agent: Build robust pipelines)
- [x] 4.  Feature Scaling & Train-Test Split (80/20 stratified split for classification, random for regression)
- [x] 5.  Baseline Model Training & Tuning (Via Optimization Agent: Fit and tune appropriate model)
- [x] 6.  Model Evaluation (Generate metrics: Classification Report or RMSE/R2 based on task type)
- [x] 7.  Pipeline Export (Save the entire trained preprocessing + model pipeline as `models/final_pipeline.pkl`)
- [x] 8.  Summary Report (Create `summary.md`)
- [x] 9.  Requirements File (Create `requirements.txt` with pinned library versions)
- [x] 10. Workspace Reorganisation (Create subfolders; move files to reduce clutter)
- [x] 11. Git Initialisation & GitHub Push (git init → .gitignore → commit → gh repo create → push)
- [x] 12. Dockerfile & Containerisation (Multi-stage Dockerfile + .dockerignore; build & test locally; push to GitHub)
- [x] 13. Render Deployment (Deploy FastAPI app from GitHub repo via render.yaml; document live endpoints)
- [ ] 14. Generic Cloud Deployment (Optional: deploy to AWS / GCP / Azure / Fly.io / Railway using Cloud Deploy Agent)

# Instructions for Initialization
Read this file, scan the workspace directory to locate the target CSV file, and read its first 5 rows. Identify the potential target variables, print them out for the user, and ask: "Which column is the target variable?". Once the user answers, immediately launch the EDA Agent to execute Step 2.

# Post-Pipeline Instructions
After completing Steps 1–7, always perform the following two finalization steps:

## Step 8 — Create `summary.md`
Create a `summary.md` file in the workspace root containing a full pipeline summary with these sections:
1. Dataset Overview (shape, quality, class balance, feature descriptions)
2. Exploratory Data Analysis (key insights, outliers, correlations, plot index)
3. Preprocessing Pipeline (steps applied, split shapes, class distribution)
4. Model Selection & Hyperparameter Tuning (all candidates, CV scores, best hyperparameters)
5. Model Evaluation (test accuracy, classification report table, confusion matrix)
6. Final Pipeline Architecture (text flow diagram)
7. Artifacts (table of all generated files with descriptions)
8. Reproducibility (Python code snippet to reload and run the final pipeline)

## Step 9 — Create `requirements.txt`
Detect the exact installed versions of all libraries used in the pipeline by running:
```python
import pandas, numpy, sklearn, joblib, matplotlib, seaborn
```
Then create `requirements.txt` in the workspace root listing each library with its pinned version. Include a header comment with the project name, generation date, and Python version. Libraries to include: `pandas`, `numpy`, `scikit-learn`, `joblib`, `matplotlib`, `seaborn`.

---

# Workspace Organisation Instructions

## Step 10 — Create Subfolders & Reorganise Files
After completing the ML pipeline (Steps 1–9), reorganise the workspace into the following folder structure to reduce clutter. Perform all moves, then update any file paths referenced inside scripts (`app.py`, `preprocess.py`, `Dockerfile`, `render.yaml`).

**Target folder structure:**
```
project-root/
├── data/               ← CSV datasets
├── models/             ← trained .pkl artifacts & .npy splits
├── plots/              ← EDA charts (.png)
├── src/                ← preprocessing & utility scripts
│   └── preprocess.py
├── tests/              ← test scripts
│   └── test_pipeline.py
├── docs/               ← all markdown documentation
│   ├── summary.md
│   ├── testing_guide.md
│   ├── test_results.md
│   ├── deployment_guide.md
│   └── docker_guide.md
├── app.py              ← stays at root (Render: uvicorn app:app requires this)
├── Dockerfile          ← stays at root (Docker & Render requirement)
├── .dockerignore       ← stays at root
├── render.yaml         ← stays at root
├── requirements.txt    ← stays at root
├── .gitignore          ← stays at root
└── CLAUDE.md           ← stays at root
```

**Steps to execute:**
1. Create `src/`, `tests/`, `docs/` directories
2. Move `preprocess.py` → `src/` (`app.py` stays at root — Render needs `uvicorn app:app`)
3. Move `test_pipeline.py` → `tests/`
4. Move all `*.md` files (except `CLAUDE.md`) → `docs/`
5. Remove any `__pycache__/` directories from root
6. Commit the reorganisation: `git add -A && git commit -m "Reorganise workspace into src/, tests/, docs/ subfolders"`

---

# Git & GitHub Instructions

## Step 11 — Initialise Git & Push to GitHub
Perform this step after the workspace is organised (Step 10).

### 11a — Check & Install GitHub CLI
```bash
gh --version        # check if installed
brew install gh     # install if missing (macOS)
gh auth status      # check login
gh auth login       # login if not authenticated (opens browser OAuth)
```

### 11b — Create `.gitignore`
Create `.gitignore` at the project root. Include:
- Python: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`
- macOS: `.DS_Store`
- IDE: `.vscode/`, `.idea/`
- Secrets: `.env`, `*.env.*`
- Logs: `*.log`

### 11c — Initialise Git & First Commit
```bash
git init
git add .
git commit -m "Initial commit: end-to-end ML pipeline with FastAPI"
```

### 11d — Create Public GitHub Repo & Push
```bash
gh repo create <project-name> \
  --public \
  --description "<brief description>" \
  --source=. \
  --remote=origin \
  --push
```
Confirm the repo is live at `https://github.com/<username>/<project-name>`.

---

# Dockerfile & Containerisation Instructions

## Step 12 — Create Dockerfile & Push to GitHub
Perform this step after the GitHub repo exists (Step 11).

### 12a — Create `Dockerfile`
Use a **multi-stage build** with `python:3.11-slim` as the base image:
- **Stage 1 (builder):** Copy `requirements.txt`, run `pip install --prefix=/install`
- **Stage 2 (runtime):** Copy installed packages from builder; copy `app.py` and `models/`; create a non-root `appuser`; expose port `8000`; set CMD with JSON array form

### 12b — Create `.dockerignore`
Exclude from the Docker build context:
- `.git/`, `__pycache__/`, `.venv/`
- `data/`, `plots/` (not needed at runtime)
- `tests/`, `docs/`, `*.md`
- `.env`, `.DS_Store`, `.claude/`

### 12c — Build & Test Locally
```bash
# Build
docker build -t <image-name>:latest .

# Run
docker run -d -p 8000:8000 --name <container-name> <image-name>:latest

# Smoke test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length_cm":5.1,"sepal_width_cm":3.5,"petal_length_cm":1.4,"petal_width_cm":0.2}'

# Stop & remove
docker stop <container-name> && docker rm <container-name>
```

### 12d — Create `docker_guide.md`
Document the following in `docs/docker_guide.md`:
- Build command
- Run command
- All test-it-live curl examples (health, single predict ×3 species, batch predict, Swagger UI)
- Post-deploy test commands (replace localhost with Render URL)
- Useful Docker commands reference table
- Image details table

### 12e — Push to GitHub
```bash
git add Dockerfile .dockerignore docs/docker_guide.md
git commit -m "Add Dockerfile, .dockerignore, and Docker guide"
git push origin main
```

---

# Render Deployment Instructions

## Step 13 — Deploy on Render
Perform this step after the Dockerfile is pushed to GitHub (Step 12).

### 13a — Create `render.yaml`
Create `render.yaml` at the project root:
```yaml
services:
  - type: web
    name: <project-name>
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.11.0"
```

### 13b — Deploy Steps
1. Go to [render.com](https://render.com) → sign up / log in with GitHub
2. Click **New +** → **Web Service**
3. Connect GitHub repo: `<username>/<project-name>`
4. Render auto-detects `render.yaml` — confirm settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
5. Click **Create Web Service** — Render builds and deploys automatically
6. Live URL: `https://<project-name>.onrender.com`

### 13c — Verify Deployment
```bash
curl https://<project-name>.onrender.com/health
curl -X POST https://<project-name>.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length_cm":5.1,"sepal_width_cm":3.5,"petal_length_cm":1.4,"petal_width_cm":0.2}'
```

### 13d — Create `deployment_guide.md`
Document the following in `docs/deployment_guide.md`:
- Prerequisites (files needed before deploying)
- 5-step Render deploy walkthrough with exact settings
- All API endpoint descriptions
- Test-it-live curl commands (health, predict, batch)
- Run locally instructions
- Input field reference table
- Free tier cold-start note

### 13e — Push deployment guide to GitHub
```bash
git add render.yaml docs/deployment_guide.md
git commit -m "Add render.yaml and deployment guide"
git push origin main
```

---

# Generic Cloud Deployment Instructions

## Step 14 — Deploy to Any Cloud Platform (via Cloud Deploy Agent)
Perform this step after the Dockerfile and GitHub repo exist (Steps 11–12). This step is **platform-agnostic** — the Cloud Deploy Agent selects the appropriate config, provisions all required infrastructure, and deploys the containerised FastAPI service automatically.

### 14a — Platform Selection
Ask the user (or auto-select based on context):

| Platform | Best For | Free Tier | Config File |
|---|---|---|---|
| **Render** | Simplest deploy from GitHub | ✅ Yes | `render.yaml` |
| **Fly.io** | Global edge, fast cold starts | ✅ Yes | `fly.toml` |
| **Railway** | One-click GitHub deploy | ✅ Yes | `railway.toml` |
| **AWS ECS (Fargate)** | Production, auto-scaling | ❌ Paid | `task-definition.json` + `ecs-service.json` |
| **AWS App Runner** | Easiest managed AWS container | ✅ Free tier | `apprunner.yaml` |
| **GCP Cloud Run** | Serverless containers, pay-per-use | ✅ Free tier | `cloudrun.yaml` |
| **Azure Container Apps** | Serverless containers on Azure | ✅ Free tier | `containerapp.yaml` |

### 14b — Prerequisites Checklist
Before deploying to any platform, verify all of the following exist:
```
✅ app.py              — FastAPI app at project root
✅ Dockerfile          — multi-stage build at project root
✅ requirements.txt    — pinned library versions
✅ models/             — final_pipeline.pkl + label_encoder.pkl
✅ .dockerignore       — excludes data/, plots/, tests/, docs/
✅ GitHub repo         — code pushed and up to date
✅ Docker image built  — verified locally with smoke tests
```

### 14c — Platform-Specific Config & Deploy Commands

#### 🟢 Render (render.yaml — already exists)
```bash
# render.yaml is already created (Step 13)
# Just connect GitHub repo at render.com → New + → Web Service
```

#### 🚁 Fly.io
```bash
# Install CLI
brew install flyctl
fly auth login

# Launch (auto-generates fly.toml)
fly launch --name <project-name> --region <region e.g. lax> --no-deploy

# Edit fly.toml — set internal_port = 8000, set [env] PORT = "8000"

# Deploy
fly deploy

# Verify
fly status
curl https://<project-name>.fly.dev/health
```
**fly.toml template:**
```toml
app = "<project-name>"
primary_region = "lax"

[build]

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

#### 🚂 Railway
```bash
# Install CLI
npm install -g @railway/cli
railway login

# Init and deploy from project root
railway init
railway up

# Set env vars if needed
railway variables set PORT=8000

# Get live URL
railway open
```
**railway.toml template:**
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

#### 🟠 AWS App Runner
```bash
# Install & configure AWS CLI
brew install awscli
aws configure   # enter Access Key, Secret, region, output format

# Push image to ECR
aws ecr create-repository --repository-name <project-name>
aws ecr get-login-password | docker login --username AWS \
  --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag <image-name>:latest \
  <account-id>.dkr.ecr.<region>.amazonaws.com/<project-name>:latest
docker push \
  <account-id>.dkr.ecr.<region>.amazonaws.com/<project-name>:latest

# Deploy App Runner service
aws apprunner create-service --cli-input-json file://apprunner.yaml
```
**apprunner.yaml template:**
```json
{
  "ServiceName": "<project-name>",
  "SourceConfiguration": {
    "ImageRepository": {
      "ImageIdentifier": "<account-id>.dkr.ecr.<region>.amazonaws.com/<project-name>:latest",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": { "PORT": "8000" }
      },
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  },
  "InstanceConfiguration": { "Cpu": "0.25 vCPU", "Memory": "0.5 GB" }
}
```

#### 🔵 GCP Cloud Run
```bash
# Install & authenticate
brew install google-cloud-sdk
gcloud auth login
gcloud config set project <project-id>

# Enable APIs
gcloud services enable run.googleapis.com containerregistry.googleapis.com

# Build & push to GCR
gcloud builds submit --tag gcr.io/<project-id>/<project-name>:latest

# Deploy
gcloud run deploy <project-name> \
  --image gcr.io/<project-id>/<project-name>:latest \
  --platform managed \
  --region <region e.g. us-central1> \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars PORT=8000

# Get live URL
gcloud run services describe <project-name> --format "value(status.url)"
```

#### 🟦 Azure Container Apps
```bash
# Install Azure CLI
brew install azure-cli
az login

# Create resource group and Container Apps environment
az group create --name <project-name>-rg --location eastus
az containerapp env create \
  --name <project-name>-env \
  --resource-group <project-name>-rg \
  --location eastus

# Build & push to Azure Container Registry
az acr create --resource-group <project-name>-rg \
  --name <project-name>acr --sku Basic
az acr login --name <project-name>acr
docker tag <image-name>:latest <project-name>acr.azurecr.io/<project-name>:latest
docker push <project-name>acr.azurecr.io/<project-name>:latest

# Deploy Container App
az containerapp create \
  --name <project-name> \
  --resource-group <project-name>-rg \
  --environment <project-name>-env \
  --image <project-name>acr.azurecr.io/<project-name>:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars PORT=8000

# Get live URL
az containerapp show \
  --name <project-name> \
  --resource-group <project-name>-rg \
  --query "properties.configuration.ingress.fqdn"
```

### 14d — Universal Smoke Tests
After deploying to any platform, run these verification commands (replace `<LIVE_URL>` with the platform's live URL):

```bash
# Health check
curl https://<LIVE_URL>/health

# Single prediction — Iris-setosa
curl -X POST https://<LIVE_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length_cm":5.1,"sepal_width_cm":3.5,"petal_length_cm":1.4,"petal_width_cm":0.2}'

# Single prediction — Iris-virginica
curl -X POST https://<LIVE_URL>/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length_cm":6.7,"sepal_width_cm":3.0,"petal_length_cm":5.2,"petal_width_cm":2.3}'

# Batch prediction
curl -X POST https://<LIVE_URL>/predict/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"sepal_length_cm":5.1,"sepal_width_cm":3.5,"petal_length_cm":1.4,"petal_width_cm":0.2},
    {"sepal_length_cm":6.7,"sepal_width_cm":3.0,"petal_length_cm":5.2,"petal_width_cm":2.3}
  ]'

# Interactive API docs
open https://<LIVE_URL>/docs
```

### 14e — Create `docs/cloud_deployment_guide.md`
Delegate to the Documentation Agent to write `docs/cloud_deployment_guide.md` with:
- Platform comparison table (Step 14a)
- Prerequisites checklist
- Step-by-step instructions for the chosen platform
- Universal smoke-test commands with the live URL filled in
- Cost / free-tier notes for the chosen platform
- Teardown / cleanup commands to avoid unexpected charges

### 14f — Push to GitHub
```bash
git add docs/cloud_deployment_guide.md
# Add any platform config files created (fly.toml, railway.toml, apprunner.yaml, etc.)
git add .
git commit -m "Add cloud deployment config and guide for <platform>"
git push origin main
```
