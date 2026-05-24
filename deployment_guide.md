# Deployment Guide — Iris Species Classification API

**Date:** 2026-05-24  
**Platform:** [Render](https://render.com) (Free Tier)  
**GitHub Repo:** [https://github.com/ramleo/iris-ml-pipeline](https://github.com/ramleo/iris-ml-pipeline)  
**API Framework:** FastAPI + Uvicorn  
**Status:** ✅ Pushed & Ready to Deploy

---

## Prerequisites

Ensure these files are present and pushed to GitHub before deploying:

| File | Purpose |
|------|---------|
| `app.py` | FastAPI application |
| `render.yaml` | Render deployment config |
| `requirements.txt` | Pinned dependencies (includes `fastapi`, `uvicorn`) |
| `models/final_pipeline.pkl` | Trained SVC pipeline |
| `models/label_encoder.pkl` | Fitted LabelEncoder |

---

## Deploy on Render

> ⏱ Estimated time: ~3 minutes

### Step 1 — Sign up / Log in
Go to [render.com](https://render.com) and sign up or log in.  
Use your **GitHub account** for the easiest setup.

### Step 2 — Create a new Web Service
Click **"New +"** → Select **"Web Service"**

### Step 3 — Connect your GitHub repository
Search for and connect: `ramleo/iris-ml-pipeline`

### Step 4 — Confirm deployment settings
Render will auto-detect `render.yaml`. Verify the following:

| Setting | Value |
|---------|-------|
| **Name** | `iris-ml-pipeline` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### Step 5 — Deploy
Click **"Create Web Service"**.  
Render will install dependencies, build, and deploy automatically.  
You'll get a live URL at: `https://iris-ml-pipeline.onrender.com`

---

## API Endpoints

Base URL: `https://iris-ml-pipeline.onrender.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | Welcome message + links |
| `/health` | `GET` | Model status and class list |
| `/predict` | `POST` | Predict species for a single sample |
| `/predict/batch` | `POST` | Predict species for up to 100 samples |
| `/docs` | `GET` | 📖 Interactive Swagger UI (try it in browser) |

---

## Test it Live

### Health Check
```bash
curl https://iris-ml-pipeline.onrender.com/health
```

**Expected response:**
```json
{
  "status": "ok",
  "model": "SVC (C=0.1, kernel=linear)",
  "classes": ["Iris-setosa", "Iris-versicolor", "Iris-virginica"],
  "version": "1.0.0"
}
```

---

### Single Prediction — Iris-setosa
```bash
curl -X POST https://iris-ml-pipeline.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length_cm": 5.1,
    "sepal_width_cm": 3.5,
    "petal_length_cm": 1.4,
    "petal_width_cm": 0.2
  }'
```

**Expected response:**
```json
{
  "predicted_species": "Iris-setosa",
  "confidence": 0.9729,
  "probabilities": {
    "Iris-setosa": 0.9729,
    "Iris-versicolor": 0.0169,
    "Iris-virginica": 0.0102
  },
  "model": "SVC (C=0.1, kernel=linear)",
  "status": "success"
}
```

---

### Single Prediction — Iris-virginica
```bash
curl -X POST https://iris-ml-pipeline.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length_cm": 6.7,
    "sepal_width_cm": 3.1,
    "petal_length_cm": 5.6,
    "petal_width_cm": 2.4
  }'
```

**Expected response:**
```json
{
  "predicted_species": "Iris-virginica",
  "confidence": 0.9924,
  "probabilities": {
    "Iris-setosa": 0.0045,
    "Iris-versicolor": 0.0032,
    "Iris-virginica": 0.9924
  },
  "model": "SVC (C=0.1, kernel=linear)",
  "status": "success"
}
```

---

### Batch Prediction (multiple samples)
```bash
curl -X POST https://iris-ml-pipeline.onrender.com/predict/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"sepal_length_cm": 5.1, "sepal_width_cm": 3.5, "petal_length_cm": 1.4, "petal_width_cm": 0.2},
    {"sepal_length_cm": 6.0, "sepal_width_cm": 2.9, "petal_length_cm": 4.5, "petal_width_cm": 1.5},
    {"sepal_length_cm": 6.7, "sepal_width_cm": 3.1, "petal_length_cm": 5.6, "petal_width_cm": 2.4}
  ]'
```

**Expected response:**
```json
{
  "count": 3,
  "predictions": [
    {"predicted_species": "Iris-setosa",     "confidence": 0.9729, "probabilities": {...}},
    {"predicted_species": "Iris-versicolor", "confidence": 0.8451, "probabilities": {...}},
    {"predicted_species": "Iris-virginica",  "confidence": 0.9924, "probabilities": {...}}
  ],
  "status": "success"
}
```

---

## Run Locally

```bash
# Clone the repo
git clone https://github.com/ramleo/iris-ml-pipeline.git
cd iris-ml-pipeline

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload

# Open interactive docs in browser
open http://127.0.0.1:8000/docs
```

---

## Input Field Reference

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `sepal_length_cm` | float | 0.1 – 20.0 | Sepal length in centimetres |
| `sepal_width_cm` | float | 0.1 – 20.0 | Sepal width in centimetres |
| `petal_length_cm` | float | 0.1 – 20.0 | Petal length in centimetres |
| `petal_width_cm` | float | 0.1 – 20.0 | Petal width in centimetres |

---

## Notes

- The free tier on Render **spins down after 15 minutes of inactivity** — the first request after idle may take ~30 seconds to wake up. Subsequent requests are instant.
- Upgrade to a paid Render plan to keep the service always-on.
- The `/docs` endpoint provides a full interactive Swagger UI — share it with anyone to let them try the API directly in their browser, no code required.

---

*Generated by Autonomous ML Agent — Claude Code (claude-sonnet-4-6)*
