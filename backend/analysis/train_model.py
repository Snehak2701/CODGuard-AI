
import pandas as pd
import numpy as np
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix
)

# ==========================================
# 1. LOAD DATA
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "orders_sample.csv"

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH)

print("\n====================================")
print("       CODGUARD AI - ML TRAINING")
print("====================================")

# ==========================================
# 2. CLEAN DATA
# ==========================================

df["final_status"] = (
    df["final_status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df = df.drop_duplicates().copy()

# Only completed orders
df = df[
    df["final_status"].isin(["DELIVERED", "RTO"])
].copy()

# Target variable
df["is_rto"] = (
    df["final_status"] == "RTO"
).astype(int)

print("\nTotal training records:", len(df))
print("Total RTO records:", df["is_rto"].sum())
print("Total delivered records:", (df["is_rto"] == 0).sum())

# ==========================================
# 3. SELECT SAFE FEATURES
# ==========================================

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

# Use only columns available in the CSV
numeric_features = [
    col for col in numeric_features if col in df.columns
]

categorical_features = [
    col for col in categorical_features if col in df.columns
]

feature_columns = numeric_features + categorical_features

if not feature_columns:
    raise ValueError("No usable input features found.")

print("\nNumeric features:", numeric_features)
print("Categorical features:", categorical_features)

# Convert numeric columns safely
for col in numeric_features:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Clean categorical values
for col in categorical_features:
    df[col] = (
        df[col]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

X = df[feature_columns].copy()
y = df["is_rto"].copy()

# ==========================================
# 4. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# ==========================================
# 5. PREPROCESSING
# ==========================================

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])

# ==========================================
# 6. DEFINE MODELS
# ==========================================

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42
    )
}

results = []
trained_models = {}

# ==========================================
# 7. TRAIN AND EVALUATE
# ==========================================

for model_name, classifier in models.items():

    print("\n------------------------------------")
    print("Training:", model_name)
    print("------------------------------------")

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, predictions)

    precision = precision_score(
        y_test, predictions, zero_division=0
    )

    recall = recall_score(
        y_test, predictions, zero_division=0
    )

    f1 = f1_score(
        y_test, predictions, zero_division=0
    )

    auc = roc_auc_score(y_test, probabilities)

    avg_precision = average_precision_score(
        y_test, probabilities
    )

    brier = brier_score_loss(
        y_test, probabilities
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {auc:.4f}")
    print(f"Average Precision: {avg_precision:.4f}")
    print(f"Brier Score: {brier:.4f}")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))

    results.append({
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": auc,
        "average_precision": avg_precision,
        "brier_score": brier
    })

    trained_models[model_name] = pipeline

# ==========================================
# 8. COMPARE MODELS
# ==========================================

results_df = pd.DataFrame(results)

print("\n====================================")
print("           MODEL COMPARISON")
print("====================================")

print(results_df.round(4).to_string(index=False))

# ==========================================
# 9. SELECT MODEL
# ==========================================

# Initial selection: highest ROC-AUC.
# Also inspect Brier score and calibration
# before using probabilities in decisions.

best_model_name = results_df.sort_values(
    by="roc_auc",
    ascending=False
).iloc[0]["model"]

best_model = trained_models[best_model_name]

# ==========================================
# 10. SAVE MODEL
# ==========================================

model_path = MODEL_DIR / "codguard_model.pkl"

joblib.dump({
    "model": best_model,
    "features": feature_columns,
    "numeric_features": numeric_features,
    "categorical_features": categorical_features,
    "model_name": best_model_name
}, model_path)

results_df.to_csv(
    MODEL_DIR / "model_comparison.csv",
    index=False
)

print("\nSelected model:", best_model_name)
print("Model saved at:", model_path)

print("\n====================================")
print("       ML TRAINING COMPLETED")
print("====================================")
