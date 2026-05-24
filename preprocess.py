"""
Preprocessing pipeline for Iris classification dataset.
Handles: feature/target separation, label encoding, scaling, train-test split,
and artifact persistence.
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "Iris.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

PIPELINE_PATH = os.path.join(MODELS_DIR, "preprocessing_pipeline.pkl")
ENCODER_PATH  = os.path.join(MODELS_DIR, "label_encoder.pkl")

# ── Load & clean ──────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df.drop(columns=["Id"], inplace=True)

FEATURE_COLS = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
TARGET_COL   = "Species"

X = df[FEATURE_COLS].values
y_raw = df[TARGET_COL].values

# ── Label-encode target ───────────────────────────────────────────────────────
le = LabelEncoder()
y = le.fit_transform(y_raw)
joblib.dump(le, ENCODER_PATH)

# ── Stratified 80/20 split ────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)

# ── Preprocessing pipeline (StandardScaler) ───────────────────────────────────
preprocessing_pipeline = Pipeline(steps=[
    ("scaler", StandardScaler())
])

X_train_scaled = preprocessing_pipeline.fit_transform(X_train)
X_test_scaled  = preprocessing_pipeline.transform(X_test)

joblib.dump(preprocessing_pipeline, PIPELINE_PATH)

# ── Persist split arrays ──────────────────────────────────────────────────────
np.save(os.path.join(MODELS_DIR, "X_train.npy"), X_train_scaled)
np.save(os.path.join(MODELS_DIR, "X_test.npy"),  X_test_scaled)
np.save(os.path.join(MODELS_DIR, "y_train.npy"), y_train)
np.save(os.path.join(MODELS_DIR, "y_test.npy"),  y_test)

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 50)
print("PREPROCESSING COMPLETE")
print("=" * 50)
print(f"\nFeature columns : {FEATURE_COLS}")
print(f"Target classes  : {list(le.classes_)} -> {list(range(len(le.classes_)))}")
print(f"\nX_train shape   : {X_train_scaled.shape}")
print(f"X_test  shape   : {X_test_scaled.shape}")
print(f"y_train shape   : {y_train.shape}")
print(f"y_test  shape   : {y_test.shape}")

print("\nClass distribution in training set:")
unique, counts = np.unique(y_train, return_counts=True)
for cls_idx, cnt in zip(unique, counts):
    print(f"  {le.classes_[cls_idx]:20s} (label {cls_idx}): {cnt} samples")

print("\nArtifacts saved:")
print(f"  {PIPELINE_PATH}")
print(f"  {ENCODER_PATH}")
for fname in ["X_train.npy", "X_test.npy", "y_train.npy", "y_test.npy"]:
    print(f"  {os.path.join(MODELS_DIR, fname)}")
print("=" * 50)
