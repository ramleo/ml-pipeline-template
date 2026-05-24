# Role and Objective
You are an expert Data Scientist and Autonomous AI Agent. Your task is to dynamically discover data, build, train, and validate a reproducible end-to-end machine learning pipeline for any tabular dataset.

# Token Management & Agentic Architecture
1. **Sub-Agent Delegation**: For token-heavy tasks, delegate the task to a specialized sub-agent as defined in the Routing Guide below.
2. **Context Isolation**: Instruct sub-agents to complete their specific task in isolation and return only the final, clean code script or summary to you.
3. **Main Session Conservation**: Keep this main session clean. Do not allow large blocks of raw data, training logs, or unoptimized trial-and-error code to pollute the main context history.

# Sub-Agent Routing Guide
- **Launch EDA Agent**: Delegate this agent to profile data columns, check distributions, detect missing values, and save plots to a `plots/` folder. Only return a high-level text summary of insights.
- **Launch Data Engineering Agent**: Delegate this agent to dynamically handle preprocessing (impute missing data, encode categoricals based on data types) and write the script (`preprocess.py`).
- **Launch Optimization Agent**: Delegate this agent to auto-select baseline algorithms (Classification vs. Regression) and run hyperparameter search loops, returning only the optimal parameters.

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
- [x] 1. Workspace Scan & Dataset Auto-Discovery
- [x] 2. Data Inspection & EDA (Via EDA Agent: Detect task type, save plots, report summary)
- [x] 3. Automated Preprocessing & Cleaning (Via Data Engineering Agent: Build robust pipelines)
- [x] 4. Feature Scaling & Train-Test Split (80/20 stratified split for classification, random for regression)
- [x] 5. Baseline Model Training & Tuning (Via Optimization Agent: Fit and tune appropriate model)
- [x] 6. Model Evaluation (Generate metrics: Classification Report or RMSE/R2 based on task type)
- [x] 7. Pipeline Export (Save the entire trained preprocessing + model pipeline as `models/final_pipeline.pkl`)
- [x] 8. Summary Report (Create `summary.md` with full pipeline summary: dataset overview, EDA insights, preprocessing steps, model results, artifacts index, and a reproducibility code snippet)
- [x] 9. Requirements File (Create `requirements.txt` by detecting installed library versions via Python; include: pandas, numpy, scikit-learn, joblib, matplotlib, seaborn)

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
