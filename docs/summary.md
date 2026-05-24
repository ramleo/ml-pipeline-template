# ML Pipeline Summary — Iris Species Classification

**Date:** 2026-05-24  
**Dataset:** `data/Iris.csv`  
**Target Variable:** `Species`  
**Task Type:** Multi-class Classification  
**Tech Stack:** Python · Pandas · Scikit-Learn · Joblib · Matplotlib · Seaborn

---

## 1. Dataset Overview

| Property | Value |
|----------|-------|
| Rows | 150 |
| Columns | 6 (5 features + 1 target) |
| Missing Values | 0 |
| Duplicate Rows | 0 |
| Classes | Iris-setosa, Iris-versicolor, Iris-virginica |
| Class Balance | Perfectly balanced — 50 samples per class (33.3% each) |

**Features used for modeling:**

| Feature | Type | Notes |
|---------|------|-------|
| `SepalLengthCm` | Float | Moderate discriminative power |
| `SepalWidthCm` | Float | Weakest discriminator; 4 mild outliers |
| `PetalLengthCm` | Float | Highly discriminative; r=0.872 with SepalLength |
| `PetalWidthCm` | Float | Highly discriminative; r=0.963 with PetalLength |

> `Id` column was dropped (row index, non-informative).

---

## 2. Exploratory Data Analysis

**Key Insights:**

- **Petal features** (`PetalLengthCm`, `PetalWidthCm`) are the most discriminative — near-zero overlap between Iris-setosa and the other two classes.
- **High multicollinearity** between PetalLength ↔ PetalWidth (r = 0.963) and SepalLength ↔ PetalLength (r = 0.872).
- **SepalWidthCm** is the weakest predictor — its distributions overlap substantially across all three classes.
- **4 mild outliers** detected in `SepalWidthCm` via IQR method; none extreme enough to require removal.
- **No preprocessing complexity** needed beyond standard scaling due to the clean, balanced dataset.

**EDA Plots saved to `plots/`:**

| Plot | Description |
|------|-------------|
| `class_distribution.png` | Bar chart of Species counts |
| `feature_distributions.png` | Histograms for all 4 features, faceted by Species |
| `correlation_heatmap.png` | Heatmap of feature correlations |
| `boxplots.png` | Boxplots of each feature grouped by Species |
| `pairplot.png` | Pairplot of all features coloured by Species |

---

## 3. Preprocessing Pipeline

**Steps applied:**

1. Dropped `Id` column
2. Separated features (X) from target (y)
3. Label-encoded `Species` → `{Iris-setosa: 0, Iris-versicolor: 1, Iris-virginica: 2}`
4. Applied `StandardScaler` to all 4 numeric features
5. Performed **80/20 stratified train-test split** (`random_state=42`)

**Split Result:**

| Split | Shape | Class Distribution |
|-------|-------|--------------------|
| Training set | (120, 4) | setosa=40, versicolor=40, virginica=40 |
| Test set | (30, 4) | setosa=10, versicolor=10, virginica=10 |

---

## 4. Model Selection & Hyperparameter Tuning

**Search method:** `GridSearchCV` — 5-fold cross-validation, `scoring='accuracy'`

**Candidates evaluated:**

| Model | Best CV Accuracy | Best Hyperparameters |
|-------|-----------------|----------------------|
| Logistic Regression | 96.67% | `C=10`, `solver=lbfgs`, `multi_class=multinomial` |
| Random Forest | 96.67% | `n_estimators=50`, `max_depth=3` |
| **SVC** ✅ | **97.50%** | **`C=0.1`, `kernel=linear`, `probability=True`** |

**Winner: Support Vector Classifier (SVC)**

---

## 5. Model Evaluation

**Test Set Accuracy: 93.33%** (28 / 30 correct)

### Classification Report

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| Iris-setosa | 1.00 | 1.00 | 1.00 | 10 |
| Iris-versicolor | 0.90 | 0.90 | 0.90 | 10 |
| Iris-virginica | 0.90 | 0.90 | 0.90 | 10 |
| **Macro avg** | **0.93** | **0.93** | **0.93** | **30** |
| **Weighted avg** | **0.93** | **0.93** | **0.93** | **30** |

### Confusion Matrix

```
                  Predicted
                  setosa  versicolor  virginica
Actual setosa     [ 10        0          0  ]   ✅ 10/10
     versicolor   [  0        9          1  ]   ⚠️  9/10
      virginica   [  0        1          9  ]   ⚠️  9/10
```

> The 2 misclassifications are boundary cases between versicolor and virginica — a well-known overlap zone in this dataset, not a model deficiency.

---

## 6. Final Pipeline Architecture

```
Raw CSV Input
     │
     ▼
 Drop 'Id' column
     │
     ▼
 StandardScaler  ──── (fitted on X_train)
     │
     ▼
 SVC(C=0.1, kernel='linear', probability=True)
     │
     ▼
 Predicted Species Label
```

---

## 7. Artifacts

| File | Description |
|------|-------------|
| `data/Iris.csv` | Source dataset |
| `preprocess.py` | Preprocessing script (reproducible) |
| `models/final_pipeline.pkl` | ✅ Complete trained pipeline (StandardScaler + SVC) |
| `models/preprocessing_pipeline.pkl` | Fitted StandardScaler pipeline |
| `models/label_encoder.pkl` | Fitted LabelEncoder |
| `models/X_train.npy` | Scaled training features (120 × 4) |
| `models/X_test.npy` | Scaled test features (30 × 4) |
| `models/y_train.npy` | Encoded training labels (120,) |
| `models/y_test.npy` | Encoded test labels (30,) |
| `plots/class_distribution.png` | EDA — class balance chart |
| `plots/feature_distributions.png` | EDA — feature histograms by class |
| `plots/correlation_heatmap.png` | EDA — feature correlation heatmap |
| `plots/boxplots.png` | EDA — boxplots by class |
| `plots/pairplot.png` | EDA — pairplot coloured by class |

---

## 8. Reproducibility

All experiments use `random_state=42` for train-test splits and model initializations. To reload and use the final pipeline:

```python
import joblib
import numpy as np

# Load the full pipeline
pipeline = joblib.load("models/final_pipeline.pkl")
label_encoder = joblib.load("models/label_encoder.pkl")

# Predict on new data (raw, unscaled)
X_new = np.array([[5.1, 3.5, 1.4, 0.2]])  # SepalLen, SepalWid, PetalLen, PetalWid
y_pred = pipeline.predict(X_new)
print(label_encoder.inverse_transform(y_pred))  # → ['Iris-setosa']
```

---

*Generated by Autonomous ML Agent — Claude Code (claude-sonnet-4-6)*
