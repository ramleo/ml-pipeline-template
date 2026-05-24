# Testing Guide — Iris Species Classification Pipeline

**Pipeline:** `models/final_pipeline.pkl`  
**Model:** SVC (`C=0.1`, `kernel=linear`)  
**Run from:** workspace root `/Users/wrks/Downloads/Claude-documentation/Test-ML/`

---

## Prerequisites

Ensure the following artifacts exist before running any test:

```
models/final_pipeline.pkl
models/label_encoder.pkl
models/X_test.npy
models/y_test.npy
data/Iris.csv
```

Install dependencies if needed:

```bash
pip install -r requirements.txt
```

---

## Option 1 — Quick Predict (Single Sample)

Paste into a Python shell or `.py` file:

```python
import joblib
import numpy as np

# Load artifacts
pipeline = joblib.load("models/final_pipeline.pkl")
le = joblib.load("models/label_encoder.pkl")

# Single sample: [SepalLengthCm, SepalWidthCm, PetalLengthCm, PetalWidthCm]
sample = np.array([[5.1, 3.5, 1.4, 0.2]])   # → should predict Iris-setosa
prediction = pipeline.predict(sample)
print("Predicted:", le.inverse_transform(prediction))

# Probabilities for each class
proba = pipeline.predict_proba(sample)
for cls, prob in zip(le.classes_, proba[0]):
    print(f"  {cls}: {prob:.2%}")
```

**Expected output:**
```
Predicted: ['Iris-setosa']
  Iris-setosa: 97.29%
  Iris-versicolor: 1.48%
  Iris-virginica: 1.23%
```

---

## Option 2 — Full Test Set Evaluation

```python
import joblib
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Load pipeline and test data
pipeline = joblib.load("models/final_pipeline.pkl")
le       = joblib.load("models/label_encoder.pkl")
X_test   = np.load("models/X_test.npy")
y_test   = np.load("models/y_test.npy")

# Evaluate
y_pred = pipeline.predict(X_test)
print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
```

> ⚠️ **Note:** `X_test.npy` is already scaled. Since the final pipeline includes `StandardScaler`, use Option 3 for a true end-to-end test with raw data.

---

## Option 3 — End-to-End Test on Raw Data ✅ Recommended

The truest test — raw CSV in, prediction out, no pre-scaling needed:

```python
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# Load
pipeline = joblib.load("models/final_pipeline.pkl")
le       = joblib.load("models/label_encoder.pkl")
df       = pd.read_csv("data/Iris.csv").drop(columns=["Id"])

# Reproduce the exact same split
X = df.drop(columns=["Species"])
y = le.transform(df["Species"])
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2,
                                         stratify=y, random_state=42)

# Predict on raw features — pipeline scales internally
y_pred = pipeline.predict(X_test)
print(f"Test Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=le.classes_))
```

---

## Option 4 — Run via Terminal (Fastest)

```bash
cd /Users/wrks/Downloads/Claude-documentation/Test-ML

python3 -c "
import joblib, numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

pipeline = joblib.load('models/final_pipeline.pkl')
le       = joblib.load('models/label_encoder.pkl')
df       = pd.read_csv('data/Iris.csv').drop(columns=['Id'])
X = df.drop(columns=['Species'])
y = le.transform(df['Species'])
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
y_pred = pipeline.predict(X_test)
print('Accuracy:', round(accuracy_score(y_test, y_pred), 4))
"
```

---

## Option 5 — Full Automated Test Suite

Run the complete test suite covering all checks:

```bash
python3 test_pipeline.py
```

This runs 6 automated checks:

| Check | Description |
|-------|-------------|
| Artifact Integrity | Verifies pipeline structure, encoder classes, split shapes |
| Single-Sample Prediction | Tests one known sample per class |
| Full Test-Set Evaluation | Accuracy, classification report, confusion matrix |
| Per-Class Accuracy | Individual accuracy per species |
| Prediction Consistency | Confirms deterministic output across runs |
| Probability Output | Validates `predict_proba` shape and row sums |

See [`test_results.md`](test_results.md) for the latest run output.

---

## Expected Results

| Metric | Expected Value |
|--------|---------------|
| Test Accuracy | **0.9333** (28/30 correct) |
| Iris-setosa | Precision 1.00 / Recall 1.00 / F1 1.00 |
| Iris-versicolor | Precision 0.90 / Recall 0.90 / F1 0.90 |
| Iris-virginica | Precision 0.90 / Recall 0.90 / F1 0.90 |
| Macro Avg F1 | **0.93** |

**Confusion Matrix:**

```
                  Predicted
                  setosa  versicolor  virginica
Actual setosa     [ 10        0          0  ]   ✅ 10/10
     versicolor   [  0        9          1  ]   ⚠️  9/10
      virginica   [  0        1          9  ]   ⚠️  9/10
```

> The 2 misclassifications are boundary cases between versicolor and virginica —
> a well-known overlap zone in the Iris dataset, not a model deficiency.

---

### To run it any time:
```
cd /Users/wrks/Downloads/Claude-documentation/Test-ML
python3 test_pipeline.py

```
*Generated by Autonomous ML Agent — Claude Code (claude-sonnet-4-6)*
