
import pandas as pd
import joblib

from pathlib import Path

# ==========================================
# 1. LOAD TRAINED MODEL
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "codguard_model.pkl"

saved_data = joblib.load(MODEL_PATH)

model = saved_data["model"]
features = saved_data["features"]

print("\n====================================")
print("       CODGUARD AI - PREDICTION")
print("====================================")

print("\nModel loaded successfully!")
print("Selected model:", saved_data["model_name"])

# ==========================================
# 2. RECEIVE NEW ORDER DETAILS
# ==========================================

new_order = {
    "order_value": 649,
    "customer_prior_orders": 2,
    "customer_prior_rto": 1,
    "state": "Karnataka",
    "city": "Bengaluru",
    "courier": "Delhivery",
    "utm_source": "meta_ads"
}

# ==========================================
# 3. CONVERT INPUT INTO DATAFRAME
# ==========================================

order_df = pd.DataFrame([new_order])

# Ensure the exact training feature order
order_df = order_df[features]

# ==========================================
# 4. PREDICT RTO PROBABILITY
# ==========================================

probabilities = model.predict_proba(order_df)

rto_probability = probabilities[0][1]

delivered_probability = probabilities[0][0]

# ==========================================
# 5. DISPLAY RESULTS
# ==========================================

print("\nNEW ORDER DETAILS")

for key, value in new_order.items():
    print(f"{key}: {value}")

print("\nPREDICTION RESULT")

print(
    f"RTO Probability: {rto_probability * 100:.2f}%"
)

print(
    f"Delivery Probability: {delivered_probability * 100:.2f}%"
)

print("\n====================================")
print("       PREDICTION COMPLETED")
print("====================================")
