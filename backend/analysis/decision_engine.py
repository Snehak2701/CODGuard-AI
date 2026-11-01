
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

# Project directories
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

# Import LLM validator
sys.path.append(str(CURRENT_DIR))
from llm_validator import validate_customer_details

# Load configuration
CONFIG_PATH = BACKEND_DIR / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)

THRESHOLDS = config["risk_thresholds"]
FINANCIAL = config["financial_assumptions"]
INTERVENTIONS = config["interventions"]
BUSINESS_RULES = config["business_rules"]

# Load ML model
MODEL_PATH = BACKEND_DIR / "models" / "codguard_model.pkl"

saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]

print("CODGuard AI decision engine initialized!")
print("ML model loaded successfully!")


# --------------------------------------------------
# 1. FINANCIAL CALCULATIONS
# --------------------------------------------------

def calculate_financials(risk):

    p = max(0.0, min(float(risk), 1.0))

    delivered_profit = FINANCIAL["delivered_gross_profit"]
    forward_cost = FINANCIAL["forward_shipping_cost"]

    # Avoid double-counting forward shipping
    if FINANCIAL["delivered_gross_profit_includes_forward_shipping"]:
        delivered_contribution = delivered_profit
    else:
        delivered_contribution = delivered_profit - forward_cost

    rto_cost = (
        FINANCIAL["forward_shipping_cost"]
        + FINANCIAL["return_shipping_cost"]
        + FINANCIAL["packaging_handling_cost"]
        + (
            FINANCIAL["product_cost"]
            * FINANCIAL["damage_probability"]
        )
    )

    # Expected contribution if the COD order is shipped
    ship_contribution = (
        (1 - p) * delivered_contribution
        - p * rto_cost
    )

    # Expected contribution if the order is cancelled
    cancel_contribution = 0.0

    # Economic break-even probability
    break_even = delivered_contribution / (
        delivered_contribution + rto_cost
    )

    # Expected contribution from a prepaid nudge
    conversion_rate = INTERVENTIONS["prepaid_conversion_rate"]
    prepaid_rto = FINANCIAL["prepaid_rto_probability"]
    discount = INTERVENTIONS["prepaid_discount"]

    prepaid_contribution = (
        (1 - prepaid_rto) * delivered_contribution
        - prepaid_rto * rto_cost
        - discount
    )

    nudge_contribution = (
        conversion_rate * prepaid_contribution
        + (1 - conversion_rate) * ship_contribution
    )

    discount_expected_cost = conversion_rate * discount

    # Illustrative WhatsApp confirmation scenario:
    # Assumes confirmation reduces RTO probability by the
    # configured proportion. This must be validated with real data.
    confirmation_reduction = INTERVENTIONS[
        "whatsapp_confirmation_success_rate"
    ]

    confirmed_risk = p * (1 - confirmation_reduction)

    confirmation_contribution = (
        (1 - confirmed_risk) * delivered_contribution
        - confirmed_risk * rto_cost
        - INTERVENTIONS["manual_review_cost_per_order"]
    )

    return {
        "predicted_rto_probability": round(p, 4),
        "delivered_contribution": round(delivered_contribution, 2),
        "expected_rto_cost": round(rto_cost, 2),
        "expected_ship_contribution": round(ship_contribution, 2),
        "expected_cancel_contribution": round(cancel_contribution, 2),
        "break_even_rto_probability": round(break_even, 4),
        "expected_prepaid_nudge_contribution": round(
            nudge_contribution, 2
        ),
        "expected_prepaid_discount_cost": round(
            discount_expected_cost, 2
        ),
        "expected_confirmation_contribution": round(
            confirmation_contribution, 2
        )
    }


# --------------------------------------------------
# 2. MACHINE LEARNING PREDICTION
# --------------------------------------------------

def predict_rto_risk(order):

    order_df = pd.DataFrame([order])

    rto_probability = model.predict_proba(order_df)[0][1]

    return round(float(rto_probability), 4)


# --------------------------------------------------
# 3. DECISION ENGINE
# --------------------------------------------------

def make_decision(risk, llm_result, order=None):

    if order is None:
        order = {}

    financials = calculate_financials(risk)

    name_quality = llm_result.get("name_quality", "UNCLEAR")
    address_quality = llm_result.get("address_quality", "UNCLEAR")

    first_time_customer = (
        order.get("customer_prior_orders", 0) == 0
    )

    # Unclear customer details require confirmation
    if name_quality == "UNCLEAR" or address_quality == "UNCLEAR":

        action = "CONFIRM_ON_WHATSAPP"
        reason = "Customer details need clarification before shipment."

    # Suspicious name or incomplete address requires review
    elif (
        name_quality == "SUSPICIOUS"
        or address_quality == "INCOMPLETE"
    ):

        action = "HOLD_FOR_REVIEW"
        reason = "Customer details require manual verification."

    # Low risk
    elif risk < THRESHOLDS["ship_as_is"]:

        action = "SHIP_AS_IS"
        reason = "Low RTO risk. Expected shipping contribution is positive."

    # Confirmation
    elif risk < THRESHOLDS["whatsapp_confirmation"]:

        action = "CONFIRM_ON_WHATSAPP"
        reason = (
            "Moderate RTO risk. Confirm customer intent "
            "before shipment."
        )

    # Prepaid nudge
    elif risk < THRESHOLDS["prepaid_nudge"]:

        action = "NUDGE_TO_PREPAID"
        reason = (
            "Higher RTO risk. Offer a prepaid discount "
            "to reduce expected return costs."
        )

    # Manual review
    else:

        action = "HOLD_FOR_REVIEW"

        if first_time_customer:
            reason = (
                "High RTO risk, but this is a first-time customer. "
                "Manual review is recommended to protect potential "
                "customer acquisition value."
            )
        elif financials["expected_ship_contribution"] < 0:
            reason = (
                "Expected shipping contribution is negative. "
                "Manual review is required before deciding."
            )
        else:
            reason = (
                "High RTO risk. Manual review is recommended "
                "before shipment."
            )

    # Automatic cancellation remains disabled
    if BUSINESS_RULES.get("never_auto_cancel", True):
        if action == "CANCEL":
            action = "HOLD_FOR_REVIEW"

    return {
        "action": action,
        "reason": reason,
        "financials": financials
    }


# --------------------------------------------------
# 4. TEST WORKFLOW
# --------------------------------------------------

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

    print("\nPredicted RTO Risk:", risk * 100, "%")

    llm_result = validate_customer_details(
        "Priya Sharma",
        "24, 3rd Main, HSR Layout, Bengaluru, Karnataka"
    )

    print("\nCustomer Validation:")
    print(json.dumps(llm_result, indent=4))

    decision = make_decision(risk, llm_result, sample_order)

    print("\nFinal Decision:")
    print("Action:", decision["action"])
    print("Reason:", decision["reason"])

    print("\nFinancial Analysis:")

    for key, value in decision["financials"].items():
        print(f"{key}: {value}")

    print("\nOrder sent for:", decision["action"])
