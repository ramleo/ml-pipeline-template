"""
test_pipeline.py — End-to-End Pipeline Test Suite
Dataset  : Iris Species Classification
Pipeline : models/final_pipeline.pkl
Run      : python3 test_pipeline.py
"""

import sys
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SEP  = "─" * 55

def section(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


# ─────────────────────────────────────────────
# 0. Load Artifacts
# ─────────────────────────────────────────────

section("0. Loading Artifacts")

try:
    pipeline = joblib.load("models/final_pipeline.pkl")
    print(f"  {PASS}  final_pipeline.pkl loaded")
except FileNotFoundError:
    print(f"  {FAIL}  models/final_pipeline.pkl not found — aborting.")
    sys.exit(1)

try:
    le = joblib.load("models/label_encoder.pkl")
    print(f"  {PASS}  label_encoder.pkl loaded")
except FileNotFoundError:
    print(f"  {FAIL}  models/label_encoder.pkl not found — aborting.")
    sys.exit(1)

try:
    df = pd.read_csv("data/Iris.csv").drop(columns=["Id"])
    print(f"  {PASS}  data/Iris.csv loaded  →  shape {df.shape}")
except FileNotFoundError:
    print(f"  {FAIL}  data/Iris.csv not found — aborting.")
    sys.exit(1)

# Reproduce the exact same 80/20 stratified split
X = df.drop(columns=["Species"])
y = le.transform(df["Species"])
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)


# ─────────────────────────────────────────────
# 1. Artifact Integrity Checks
# ─────────────────────────────────────────────

section("1. Artifact Integrity Checks")

# Pipeline has 2 named steps
steps = list(pipeline.named_steps.keys())
if len(steps) == 2:
    print(f"  {PASS}  Pipeline has 2 steps: {steps}")
else:
    print(f"  {FAIL}  Expected 2 pipeline steps, found {len(steps)}: {steps}")

# LabelEncoder knows all 3 classes
expected_classes = {"Iris-setosa", "Iris-versicolor", "Iris-virginica"}
if set(le.classes_) == expected_classes:
    print(f"  {PASS}  LabelEncoder classes: {list(le.classes_)}")
else:
    print(f"  {FAIL}  Unexpected classes: {list(le.classes_)}")

# Test split shape
if X_test_raw.shape == (30, 4) and len(y_test) == 30:
    print(f"  {PASS}  Test split shape: X={X_test_raw.shape}, y={y_test.shape}")
else:
    print(f"  {FAIL}  Unexpected test split shape: X={X_test_raw.shape}")


# ─────────────────────────────────────────────
# 2. Single-Sample Prediction
# ─────────────────────────────────────────────

section("2. Single-Sample Prediction")

samples = {
    "Iris-setosa"    : np.array([[5.1, 3.5, 1.4, 0.2]]),
    "Iris-versicolor": np.array([[6.0, 2.9, 4.5, 1.5]]),
    "Iris-virginica" : np.array([[6.7, 3.1, 5.6, 2.4]]),
}

all_correct = True
for expected_label, sample in samples.items():
    pred_encoded = pipeline.predict(sample)
    pred_label   = le.inverse_transform(pred_encoded)[0]
    proba        = pipeline.predict_proba(sample)[0]
    confidence   = proba.max()
    status       = PASS if pred_label == expected_label else FAIL
    if pred_label != expected_label:
        all_correct = False
    print(f"  {status}  Input {sample[0].tolist()}")
    print(f"          → Predicted: {pred_label:<20} Confidence: {confidence:.2%}")

if all_correct:
    print(f"\n  {PASS}  All 3 known samples predicted correctly.")


# ─────────────────────────────────────────────
# 3. Full Test-Set Evaluation
# ─────────────────────────────────────────────

section("3. Full Test-Set Evaluation  (30 samples)")

y_pred    = pipeline.predict(X_test_raw)
accuracy  = accuracy_score(y_test, y_pred)
threshold = 0.90

status = PASS if accuracy >= threshold else FAIL
print(f"  {status}  Test Accuracy: {accuracy:.4f}  (threshold ≥ {threshold})")

print("\n  Classification Report:")
report = classification_report(
    y_test, y_pred,
    target_names=le.classes_,
    digits=2
)
for line in report.splitlines():
    print(f"    {line}")

print("\n  Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
header = f"    {'':22}" + "  ".join(f"{c[:12]:<12}" for c in le.classes_)
print(header)
for cls, row in zip(le.classes_, cm):
    print(f"    {cls:<22}  " + "  ".join(f"{v:<12}" for v in row))


# ─────────────────────────────────────────────
# 4. Per-Class Accuracy
# ─────────────────────────────────────────────

section("4. Per-Class Accuracy")

for i, cls in enumerate(le.classes_):
    mask        = y_test == i
    cls_acc     = accuracy_score(y_test[mask], y_pred[mask])
    status      = PASS if cls_acc >= 0.80 else FAIL
    correct     = int(cls_acc * mask.sum())
    print(f"  {status}  {cls:<22}  {correct}/{mask.sum()}  ({cls_acc:.0%})")


# ─────────────────────────────────────────────
# 5. Prediction Consistency Check
# ─────────────────────────────────────────────

section("5. Prediction Consistency  (re-run same input)")

pred_run1 = pipeline.predict(X_test_raw)
pred_run2 = pipeline.predict(X_test_raw)

if np.array_equal(pred_run1, pred_run2):
    print(f"  {PASS}  Predictions are deterministic across two runs.")
else:
    print(f"  {FAIL}  Predictions differ between runs — non-determinism detected.")


# ─────────────────────────────────────────────
# 6. Probability Output Check
# ─────────────────────────────────────────────

section("6. Probability Output Check")

probas = pipeline.predict_proba(X_test_raw)
sums   = probas.sum(axis=1)

if probas.shape == (30, 3):
    print(f"  {PASS}  predict_proba shape: {probas.shape}")
else:
    print(f"  {FAIL}  Unexpected proba shape: {probas.shape}")

if np.allclose(sums, 1.0, atol=1e-6):
    print(f"  {PASS}  All probability rows sum to 1.0")
else:
    print(f"  {FAIL}  Probability rows do not sum to 1.0: {sums[:5]}")


# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────

section("TEST SUMMARY")

total_tests = 10
print(f"  Pipeline     : SVC (C=0.1, kernel=linear)")
print(f"  Test samples : 30  (stratified 80/20 split, random_state=42)")
print(f"  Accuracy     : {accuracy:.4f}")
print(f"  Status       : {'ALL CHECKS PASSED 🎉' if accuracy >= threshold else 'SOME CHECKS FAILED — review output above'}")
print(f"\n{SEP}\n")
