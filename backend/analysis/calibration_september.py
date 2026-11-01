
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    brier_score_loss,
    log_loss,
    roc_auc_score
)

# File paths
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

REPLAY_PATH = (
    BACKEND_DIR / "data" / "september_2026_replay.csv"
)

# Load September replay
df = pd.read_csv(REPLAY_PATH)

# Actual outcomes: RTO = 1, Delivered = 0
df["actual_rto"] = (
    df["final_status"].str.upper() == "RTO"
).astype(int)

y_true = df["actual_rto"]
y_prob = df["predicted_rto_probability"]

# Overall calibration metrics
brier = brier_score_loss(y_true, y_prob)
logloss = log_loss(y_true, y_prob)
auc = roc_auc_score(y_true, y_prob)

print("\n===== SEPTEMBER MODEL CALIBRATION =====")

print(f"Total orders: {len(df)}")
print(f"Actual RTO rate: {y_true.mean() * 100:.2f}%")
print(f"Average predicted RTO risk: {y_prob.mean() * 100:.2f}%")

print("\nCalibration Metrics:")
print(f"Brier Score: {brier:.4f}")
print(f"Log Loss: {logloss:.4f}")
print(f"ROC-AUC: {auc:.4f}")

# Group predicted probabilities into risk bands
bins = [0, 0.20, 0.40, 0.60, 0.70, 1.001]

labels = [
    "0-20%",
    "20-40%",
    "40-60%",
    "60-70%",
    "70-100%"
]

df["risk_band"] = pd.cut(
    y_prob,
    bins=bins,
    labels=labels,
    right=False
)

calibration = (
    df.groupby("risk_band", observed=False)
    .agg(
        orders=("actual_rto", "count"),
        actual_rto_rate=("actual_rto", "mean"),
        average_predicted_risk=(
            "predicted_rto_probability", "mean"
        )
    )
)

calibration["actual_rto_rate"] *= 100
calibration["average_predicted_risk"] *= 100

print("\n===== RISK BAND CALIBRATION =====")
print(calibration.round(2))

# Save report
output_path = (
    BACKEND_DIR / "data" / "september_calibration_report.csv"
)

calibration.to_csv(output_path)

print("\nCalibration report saved to:")
print(output_path)
