
from decision_engine import predict_rto_risk, make_decision
from llm_validator import validate_customer_details

from whatsapp_simulator import (
    get_confirmation_message,
    get_prepaid_message,
    process_customer_response
)

import json
from pathlib import Path


# Load configuration
BACKEND_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BACKEND_DIR / "config.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)


def run_codguard(order):

    print("\n========== CODGUARD AI ==========")

    # Step 1: Predict RTO risk
    risk = predict_rto_risk(order)

    print(f"\nPredicted RTO Risk: {risk * 100:.2f}%")

    # Step 2: Validate customer details
    llm_result = validate_customer_details(
        order["customer_name"],
        order["address"]
    )

    print("\nCustomer Validation:")
    print(json.dumps(llm_result, indent=4))

    # Step 3: Make financially informed decision
    decision = make_decision(risk, llm_result, order)

    print("\nFinal Decision:")
    print("Action:", decision["action"])
    print("Reason:", decision["reason"])

    # Step 4: Display financial analysis
    financials = decision["financials"]

    print("\nFinancial Analysis:")
    print(
        "Expected contribution if shipped: ₹",
        financials["expected_ship_contribution"]
    )
    print(
        "Expected contribution if cancelled: ₹",
        financials["expected_cancel_contribution"]
    )
    print(
        "Expected RTO cost: ₹",
        financials["expected_rto_cost"]
    )
    print(
        "Break-even RTO risk:",
        financials["break_even_rto_probability"] * 100,
        "%"
    )
    print(
        "Expected prepaid-nudge contribution: ₹",
        financials["expected_prepaid_nudge_contribution"]
    )
    print(
        "Expected confirmation contribution: ₹",
        financials["expected_confirmation_contribution"]
    )

    # Step 5: Generate relevant customer message
    action = decision["action"]

    if action == "CONFIRM_ON_WHATSAPP":

        message = get_confirmation_message(
            order["customer_name"],
            order["order_id"],
            order.get("language", "English")
        )

        print("\nWhatsApp Confirmation Message:")
        print(message)

    elif action == "NUDGE_TO_PREPAID":

        discount = config["interventions"]["prepaid_discount"]

        message = get_prepaid_message(
            order["customer_name"],
            order["order_id"],
            discount
        )

        print("\nWhatsApp Prepaid Offer:")
        print(message)

    elif action == "HOLD_FOR_REVIEW":

        print("\nOrder sent for manual review.")
        print("No automatic cancellation has been performed.")

    elif action == "SHIP_AS_IS":

        print("\nOrder approved for shipping.")

    # Step 6: Return complete result
    return {
        "order_id": order["order_id"],
        "rto_probability": risk,
        "llm_validation": llm_result,
        "decision": decision
    }


# Test the complete workflow
if __name__ == "__main__":

    sample_order = {
        "order_id": "CG101",
        "customer_name": "Priya Sharma",
        "address": "24, 3rd Main, HSR Layout, Bengaluru, Karnataka",
        "language": "English",
        "order_value": 649,
        "customer_prior_orders": 2,
        "customer_prior_rto": 1,
        "state": "Karnataka",
        "city": "Bengaluru",
        "courier": "Delhivery",
        "utm_source": "meta_ads"
    }

    result = run_codguard(sample_order)
