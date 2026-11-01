
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    brier_score_loss,
    log_loss,
    confusion_matrix
)

# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

DATA_PATH = BACKEND_DIR / "data" / "orders_sample.csv"

df = pd.read_csv(DATA_PATH)
df = df.drop_duplicates().copy()

df["final_status"] = (
    df["final_status"].astype(str).str.strip().str.upper()
)

df = df[
    df["final_status"].isin(["DELIVERED", "RTO"])
].copy()

df["order_datetime"] = pd.to_datetime(
    df["order_datetime"], errors="coerce"
)

df = df.dropna(subset=["order_datetime"])

df["is_rto"] = (
    df["final_status"] == "RTO"
).astype(int)

df = df.sort_values("order_datetime").reset_index(drop=True)


# --------------------------------------------------
# 2. SELECT FEATURES
# --------------------------------------------------

numeric_features = [
    "order_value",
    "customer_prior_orders",
    "customer_prior_rto"
]

categorical_features = [
    "state",
    "city",
    "courier",
    "utm_source"
]

features = numeric_features + categorical_features

X = df[features]
y = df["is_rto"]


# --------------------------------------------------
# 3. CHRONOLOGICAL TRAIN/TEST SPLIT
# --------------------------------------------------

unique_dates = np.sort(
    df["order_datetime"].dt.normalize().unique()
)

if len(unique_dates) < 2:
    raise ValueError("Not enough distinct dates for time-based validation.")

split_index = int(len(unique_dates) * 0.80)
split_index = min(max(split_index, 1), len(unique_dates) - 1)

cutoff_date = unique_dates[split_index]

train_mask = (
    df["order_datetime"].dt.normalize() < cutoff_date
)

test_mask = ~train_mask

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("\n===== TIME-BASED DATA SPLIT =====")
print("Training orders:", len(X_train))
print("Testing orders:", len(X_test))
print("Training period:",
      df.loc[train_mask, "order_datetime"].min(),
      "to",
      df.loc[train_mask, "order_datetime"].max())

print("Testing period:",
      df.loc[test_mask, "order_datetime"].min(),
      "to",
      df.loc[test_mask, "order_datetime"].max())


# --------------------------------------------------
# 4. BUILD MODEL PIPELINE
# --------------------------------------------------

numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])


# --------------------------------------------------
# 5. TRAIN USING ONLY OLDER ORDERS
# --------------------------------------------------

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 6. EVALUATE MODEL
# --------------------------------------------------

print("\n===== TIME-BASED MODEL PERFORMANCE =====")

print("Accuracy:",
      round(accuracy_score(y_test, y_pred), 4))

print("RTO Precision:",
      round(precision_score(y_test, y_pred, zero_division=0), 4))

print("RTO Recall:",
      round(recall_score(y_test, y_pred, zero_division=0), 4))

print("F1 Score:",
      round(f1_score(y_test, y_pred, zero_division=0), 4))

if y_test.nunique() == 2:
    print("ROC-AUC:",
          round(roc_auc_score(y_test, y_prob), 4))

print("Brier Score:",
      round(brier_score_loss(y_test, y_prob), 4))

print("Log Loss:",
      round(log_loss(y_test, y_prob, labels=[0, 1]), 4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=[0, 1]))


# --------------------------------------------------
# 7. BASELINE COMPARISON
# --------------------------------------------------

baseline_probability = y_train.mean()

baseline_predictions = np.full(
    len(y_test), baseline_probability
)

print("\n===== BASELINE COMPARISON =====")

print("Training-period RTO rate:",
      round(baseline_probability * 100, 2), "%")

print("Model Brier Score:",
      round(brier_score_loss(y_test, y_prob), 4))

print("Baseline Brier Score:",
      round(brier_score_loss(y_test, baseline_predictions), 4))


# --------------------------------------------------
# 8. RISK BAND CALIBRATION
# --------------------------------------------------

test_results = df.loc[test_mask].copy()

test_results["predicted_rto_probability"] = y_prob

test_results["risk_band"] = pd.cut(
    y_prob,
    bins=[0, 0.20, 0.40, 0.60, 0.70, 1.001],
    labels=[
        "0-20%",
        "20-40%",
        "40-60%",
        "60-70%",
        "70-100%"
    ],
    right=False
)

calibration = (
    test_results.groupby("risk_band", observed=False)
    .agg(
        orders=("is_rto", "count"),
        actual_rto_rate=("is_rto", "mean"),
        average_predicted_risk=(
            "predicted_rto_probability", "mean"
        )
    )
)

calibration["actual_rto_rate"] *= 100
calibration["average_predicted_risk"] *= 100

print("\n===== TEST SET CALIBRATION =====")
print(calibration.round(2))


# --------------------------------------------------
# 9. SAVE RESULTS WITHOUT OVERWRITING OLD MODEL
# --------------------------------------------------

MODEL_OUTPUT = (
    BACKEND_DIR / "models" / "codguard_time_validated_model.pkl"
)

RESULT_OUTPUT = (
    BACKEND_DIR / "data" / "time_based_test_results.csv"
)

CALIBRATION_OUTPUT = (
    BACKEND_DIR / "data" / "time_based_calibration.csv"
)

joblib.dump(model, MODEL_OUTPUT)

test_results.to_csv(RESULT_OUTPUT, index=False)
calibration.to_csv(CALIBRATION_OUTPUT)

print("\nFiles saved successfully:")
print(MODEL_OUTPUT)
print(RESULT_OUTPUT)
print(CALIBRATION_OUTPUT)
