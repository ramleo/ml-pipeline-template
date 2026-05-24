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

## Sub-Agent Roster (see local CLAUDE.md files for full specs)

| Agent | Trigger | Local spec |
|---|---|---|
| 🔬 EDA Agent | Step 2 — EDA | @src/CLAUDE.md |
| ⚙️ Data Engineering Agent | Step 3 — Preprocessing | @src/CLAUDE.md |
| 🏆 Optimization Agent | Steps 4–6 — Training | @src/CLAUDE.md |
| 🌐 FastAPI Agent | API development | @src/CLAUDE.md |
| 🐳 Docker Agent | Step 12 — Docker | @deploy/CLAUDE.md |
| 📄 Documentation Agent | Steps 8, docs | @docs/CLAUDE.md |
| 🧪 Testing Agent | After pipeline | @tests/CLAUDE.md |
| 🚀 Git & Deploy Agent | Steps 11–13 | @deploy/CLAUDE.md |
| ☁️ Cloud Deploy Agent | Step 14 — Cloud | @deploy/CLAUDE.md |

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
