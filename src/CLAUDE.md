# src/CLAUDE.md — Data Pipeline Agent Specs & Post-Pipeline Steps

## 🔬 EDA Agent
**Trigger:** Step 2 — Data Inspection & EDA
**Delegate when:** Profiling columns, plotting distributions, computing correlations, detecting outliers.
**Input to provide:** CSV file path, target variable name, task type.
**Agent must:** Save all plots to `plots/`; return ONLY a bullet-point text summary (no raw data, no code).
**Returns:** Dataset shape, quality issues, class balance, top feature insights, outlier summary, correlation highlights.

---

## ⚙️ Data Engineering Agent
**Trigger:** Step 3 — Automated Preprocessing & Cleaning
**Delegate when:** Building preprocessing pipelines, encoding categoricals, imputing missing values, writing `src/preprocess.py`.
**Input to provide:** CSV path, target column, EDA summary (key data types, missing value counts, outlier findings).
**Agent must:** Write the complete `src/preprocess.py` script and execute it; return ONLY confirmation + printed output (split shapes, class distribution). Do not return the full script.
**Returns:** Confirmation that script ran, split shapes, class distribution, paths of saved artifacts.

---

## 🏆 Optimization Agent
**Trigger:** Steps 4–6 — Feature Scaling, Model Training & Evaluation
**Delegate when:** Running GridSearchCV, fitting multiple candidate models, evaluating on test set.
**Input to provide:** Paths to saved `.npy` splits, label encoder path, candidate algorithms and hyperparameter grids, task type.
**Agent must:** Run full hyperparameter search, select best model, build final pipeline, save to `models/final_pipeline.pkl`, evaluate on test set; return ONLY the results table and metrics.
**Returns:** Best model name, optimal hyperparameters, CV accuracy, test accuracy, classification report, confusion matrix, confirmation that `final_pipeline.pkl` was saved.

---

## 🌐 FastAPI Agent
**Trigger:** API development task
**Delegate when:** Writing or expanding the FastAPI `app.py` (new endpoints, input validation, response schemas, batch prediction).
**Input to provide:** Model path, label encoder path, list of endpoints to create with expected request/response shapes.
**Agent must:** Write the complete `app.py`, start the server, smoke-test all endpoints via curl, return ONLY confirmation + curl responses. Do not return the full script.
**Returns:** Confirmation all endpoints respond correctly, sample curl outputs, any errors encountered.

---

## Step 8 — Create `summary.md`
After completing Steps 1–7, create `docs/summary.md` with these sections:
1. Dataset Overview (shape, quality, class balance, feature descriptions)
2. Exploratory Data Analysis (key insights, outliers, correlations, plot index)
3. Preprocessing Pipeline (steps applied, split shapes, class distribution)
4. Model Selection & Hyperparameter Tuning (all candidates, CV scores, best hyperparameters)
5. Model Evaluation (test accuracy, classification report table, confusion matrix)
6. Final Pipeline Architecture (text flow diagram)
7. Artifacts (table of all generated files with descriptions)
8. Reproducibility (Python code snippet to reload and run the final pipeline)

---

## Step 9 — Create `requirements.txt`
Detect the exact installed versions of all libraries used in the pipeline by running:
```python
import pandas, numpy, sklearn, joblib, matplotlib, seaborn
```
Create `requirements.txt` in the workspace root listing each library with its pinned version. Include a header comment with the project name, generation date, and Python version. Libraries to include: `pandas`, `numpy`, `scikit-learn`, `joblib`, `matplotlib`, `seaborn`.

---

## Step 10 — Create Subfolders & Reorganise Files
After completing the ML pipeline (Steps 1–9), reorganise the workspace. Perform all moves, then update any file paths referenced inside scripts (`app.py`, `preprocess.py`, `Dockerfile`, `render.yaml`).

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
