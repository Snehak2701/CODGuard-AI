
import pandas as pd
import joblib
from pathlib import Path

# Project paths
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

DATA_PATH = BACKEND_DIR / "data" / "orders_sample.csv"
MODEL_PATH = BACKEND_DIR / "models" / "codguard_model.pkl"
OUTPUT_PATH = BACKEND_DIR / "data" / "september_2026_replay.csv"

# Load data and model
df = pd.read_csv(DATA_PATH)
saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]

# Clean historical data
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

# Select September 2026
df = df[
    (df["order_datetime"] >= "2026-09-01")
    & (df["order_datetime"] < "2026-10-01")
].copy()

# Model features
features = [
    "order_value",
    "customer_prior_orders",
    "customer_prior_rto",
    "state",
    "city",
    "courier",
    "utm_source"
]

# Predict RTO probability
df["predicted_rto_probability"] = model.predict_proba(
    df[features]
)[:, 1]

# Assign decision
def assign_action(risk):

    if risk < 0.20:
        return "SHIP_AS_IS"

    elif risk < 0.40:
        return "CONFIRM_ON_WHATSAPP"

    elif risk < 0.60:
        return "NUDGE_TO_PREPAID"

    else:
        return "HOLD_FOR_REVIEW"


df["decision_action"] = (
    df["predicted_rto_probability"].apply(assign_action)
)

# Display results
print("\n===== SEPTEMBER 2026 HISTORICAL REPLAY =====")

print("\nTotal Orders:", len(df))

print("\nActual Outcomes:")
print(df["final_status"].value_counts())

print("\nDecision Distribution:")
print(
    df["decision_action"]
    .value_counts()
    .reindex([
        "SHIP_AS_IS",
        "CONFIRM_ON_WHATSAPP",
        "NUDGE_TO_PREPAID",
        "HOLD_FOR_REVIEW"
    ], fill_value=0)
)

# Actual RTO rates by action
print("\nActual RTO Rate by Decision:")

print(
    df.groupby("decision_action", observed=False)
    .agg(
        orders=("order_id", "count"),
        actual_rtos=(
            "final_status",
            lambda x: (x == "RTO").sum()
        ),
        average_predicted_risk=(
            "predicted_rto_probability", "mean"
        )
    )
)

# Save replay
df.to_csv(OUTPUT_PATH, index=False)

print("\nReplay file saved to:")
print(OUTPUT_PATH)
