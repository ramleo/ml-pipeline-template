"""
app.py — FastAPI REST API for Iris Species Classification
Run locally : uvicorn app:app --reload
Docs        : http://127.0.0.1:8000/docs
"""

import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────

app = FastAPI(
    title="Iris Species Classifier",
    description=(
        "End-to-end ML API for classifying Iris flower species "
        "(setosa, versicolor, virginica) from sepal and petal measurements. "
        "Model: SVC (C=0.1, kernel=linear) — Test Accuracy: 93.33%"
    ),
    version="1.0.0",
)

# ─────────────────────────────────────────────
# Load artifacts at startup
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    pipeline = joblib.load(os.path.join(BASE_DIR, "models", "final_pipeline.pkl"))
    le       = joblib.load(os.path.join(BASE_DIR, "models", "label_encoder.pkl"))
except FileNotFoundError as e:
    raise RuntimeError(f"Model artifact not found: {e}")


# ─────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────

class IrisFeatures(BaseModel):
    sepal_length_cm: float = Field(..., ge=0.1, le=20.0, example=5.1,
                                   description="Sepal length in centimetres")
    sepal_width_cm:  float = Field(..., ge=0.1, le=20.0, example=3.5,
                                   description="Sepal width in centimetres")
    petal_length_cm: float = Field(..., ge=0.1, le=20.0, example=1.4,
                                   description="Petal length in centimetres")
    petal_width_cm:  float = Field(..., ge=0.1, le=20.0, example=0.2,
                                   description="Petal width in centimetres")

    @field_validator("*", mode="before")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("All measurements must be positive numbers.")
        return v


class PredictionResponse(BaseModel):
    predicted_species: str
    confidence:        float
    probabilities:     dict[str, float]
    model:             str
    status:            str


class HealthResponse(BaseModel):
    status:  str
    model:   str
    classes: list[str]
    version: str


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    """API root — returns a welcome message and links."""
    return {
        "message": "🌸 Iris Species Classifier API",
        "docs":    "/docs",
        "health":  "/health",
        "predict": "/predict",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    """Check that the API and model are loaded and ready."""
    return HealthResponse(
        status  = "ok",
        model   = "SVC (C=0.1, kernel=linear)",
        classes = list(le.classes_),
        version = "1.0.0",
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(features: IrisFeatures):
    """
    Predict the Iris species from sepal and petal measurements.

    - **sepal_length_cm** — Sepal length in cm
    - **sepal_width_cm**  — Sepal width in cm
    - **petal_length_cm** — Petal length in cm
    - **petal_width_cm**  — Petal width in cm

    Returns the predicted species, confidence score, and per-class probabilities.
    """
    try:
        X = np.array([[
            features.sepal_length_cm,
            features.sepal_width_cm,
            features.petal_length_cm,
            features.petal_width_cm,
        ]])

        pred_encoded = pipeline.predict(X)[0]
        pred_label   = le.inverse_transform([pred_encoded])[0]
        probas       = pipeline.predict_proba(X)[0]
        confidence   = float(probas.max())
        prob_dict    = {cls: round(float(p), 4) for cls, p in zip(le.classes_, probas)}

        return PredictionResponse(
            predicted_species = pred_label,
            confidence        = round(confidence, 4),
            probabilities     = prob_dict,
            model             = "SVC (C=0.1, kernel=linear)",
            status            = "success",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Prediction"])
def predict_batch(samples: list[IrisFeatures]):
    """
    Predict species for multiple samples in one request (max 100).
    """
    if len(samples) > 100:
        raise HTTPException(status_code=400, detail="Batch size must not exceed 100 samples.")
    if len(samples) == 0:
        raise HTTPException(status_code=400, detail="Batch must contain at least 1 sample.")

    try:
        X = np.array([[
            s.sepal_length_cm, s.sepal_width_cm,
            s.petal_length_cm, s.petal_width_cm,
        ] for s in samples])

        preds  = pipeline.predict(X)
        probas = pipeline.predict_proba(X)
        labels = le.inverse_transform(preds)

        results = []
        for label, proba in zip(labels, probas):
            results.append({
                "predicted_species": label,
                "confidence":        round(float(proba.max()), 4),
                "probabilities":     {cls: round(float(p), 4)
                                      for cls, p in zip(le.classes_, proba)},
            })

        return {"count": len(results), "predictions": results, "status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
