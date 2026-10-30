
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

# Get project directories
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

# Import LLM validator
sys.path.append(str(CURRENT_DIR))
from llm_validator import validate_customer_details

# Load configuration
CONFIG_PATH = BACKEND_DIR / "config.json"

with open(CONFIG_PATH, "r") as file:
    config = json.load(file)

THRESHOLDS = config["risk_thresholds"]

# Load trained ML model
MODEL_PATH = BACKEND_DIR / "models" / "codguard_model.pkl"

saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]

print("CODGuard AI decision engine initialized!")
print("ML model loaded successfully!")



def predict_rto_risk(order):

    # Convert order details into a DataFrame
    order_df = pd.DataFrame([order])

    # Get RTO probability from the trained model
    rto_probability = model.predict_proba(order_df)[0][1]

    return round(float(rto_probability), 4)


def make_decision(risk, llm_result):

    name_quality = llm_result["name_quality"]
    address_quality = llm_result["address_quality"]

    # Incomplete or uncertain customer details
    if name_quality == "UNCLEAR" or address_quality == "UNCLEAR":
        return {
            "action": "CONFIRM_ON_WHATSAPP",
            "reason": "Customer details need clarification."
        }

    # Suspicious name or incomplete address
    if name_quality == "SUSPICIOUS" or address_quality == "INCOMPLETE":
        return {
            "action": "HOLD_FOR_REVIEW",
            "reason": "Customer details need manual verification."
        }

    if risk < THRESHOLDS["ship_as_is"]:
        return {
            "action": "SHIP_AS_IS",
            "reason": "Low predicted RTO risk and valid customer details."
        }

    elif risk < THRESHOLDS["whatsapp_confirmation"]:
        return {
            "action": "CONFIRM_ON_WHATSAPP",
            "reason": "Moderate RTO risk. Confirm customer intent."
        }

    elif risk < THRESHOLDS["prepaid_nudge"]:
        return {
            "action": "NUDGE_TO_PREPAID",
            "reason": "High RTO risk. Encourage prepaid payment."
        }

    else:
        return {
            "action": "HOLD_FOR_REVIEW",
            "reason": "Very high RTO risk. Manual review required."
        }


    name_quality = llm_result["name_quality"]
    address_quality = llm_result["address_quality"]

    # Rule 1: Unclear AI result or incomplete details
    if name_quality == "UNCLEAR" or address_quality == "UNCLEAR":
        return {
            "action": "CONFIRM_ON_WHATSAPP",
            "reason": "Customer details need clarification."
        }

    # Rule 2: Suspicious name or incomplete address
    if name_quality == "SUSPICIOUS" or address_quality == "INCOMPLETE":
        return {
            "action": "HOLD_FOR_REVIEW",
            "reason": "Customer name or address needs manual verification."
        }

    # Rule 3: Low RTO risk
    if risk < 0.20:
        return {
            "action": "SHIP_AS_IS",
            "reason": "Low predicted RTO risk and valid customer details."
        }

    # Rule 4: Medium RTO risk
    elif risk < 0.40:
        return {
            "action": "CONFIRM_ON_WHATSAPP",
            "reason": "Moderate predicted RTO risk. Confirm customer intent."
        }

    # Rule 5: High RTO risk
    elif risk < 0.65:
        return {
            "action": "NUDGE_TO_PREPAID",
            "reason": "High predicted RTO risk. Encourage prepaid payment."
        }

    # Rule 6: Very high RTO risk
    else:
        return {
            "action": "HOLD_FOR_REVIEW",
            "reason": "Very high predicted RTO risk. Manual review required."
        }

# Test order

if __name__ == "__main__":

    sample_order = {
        "order_value": 649,
        "customer_prior_orders": 2,
        "customer_prior_rto": 1,
        "state": "Karnataka",
        "city": "Bengaluru",
        "courier": "Delhivery",
        "utm_source": "meta_ads"
    }

    risk = predict_rto_risk(sample_order)

    print("\nOrder RTO Risk:", risk * 100, "%")

    llm_result = validate_customer_details(
        "Priya Sharma",
        "24, 3rd Main, HSR Layout, Bengaluru, Karnataka"
    )

    print("\nLLM Validation:")
    print(llm_result)

    decision = make_decision(risk, llm_result)

    print("\nCODGuard Decision:")
    print("Action:", decision["action"])
    print("Reason:", decision["reason"])

