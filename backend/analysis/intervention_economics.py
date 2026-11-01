
import json
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

INPUT_PATH = BACKEND_DIR / "data" / "time_based_test_results.csv"
CONFIG_PATH = BACKEND_DIR / "config.json"
OUTPUT_PATH = BACKEND_DIR / "data" / "intervention_economics.csv"

# --------------------------------------------------
# 2. LOAD DATA AND CONFIGURATION
# --------------------------------------------------

df = pd.read_csv(INPUT_PATH)

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    config = json.load(file)

risk = df["predicted_rto_probability"].astype(float)
actual_rto = df["is_rto"].astype(int)

financial = config["financial_assumptions"]
interventions = config["interventions"]

rto_cost = (
    financial["forward_shipping_cost"]
    + financial["return_shipping_cost"]
    + financial["packaging_handling_cost"]
    + financial["product_cost"] * financial["damage_probability"]
)

prepaid_rto = financial["prepaid_rto_probability"]
prepaid_discount = interventions["prepaid_discount"]
prepaid_conversion = interventions["prepaid_conversion_rate"]

# The existing project interprets this as a relative reduction
# in RTO probability after WhatsApp confirmation.
whatsapp_reduction = interventions[
    "whatsapp_confirmation_success_rate"
]

# --------------------------------------------------
# 3. ASSIGN ORDERS TO EXISTING ACTION BANDS
# --------------------------------------------------

def assign_bucket(probability):
    if probability < 0.20:
        return "SHIP_AS_IS"
    elif probability < 0.40:
        return "WHATSAPP_CONFIRMATION"
    elif probability < 0.60:
        return "PREPAID_NUDGE"
    else:
        return "HOLD_FOR_REVIEW"


df["action"] = risk.apply(assign_bucket)

# --------------------------------------------------
# 4. SIMULATE EACH INTERVENTION
# --------------------------------------------------

results = []

for action in [
    "SHIP_AS_IS",
    "WHATSAPP_CONFIRMATION",
    "PREPAID_NUDGE",
    "HOLD_FOR_REVIEW"
]:

    group = df[df["action"] == action].copy()

    order_count = len(group)

    if order_count == 0:
        continue

    baseline_expected_rto = (
        group["predicted_rto_probability"].sum()
    )

    actual_rto_count = int(group["is_rto"].sum())

    expected_rto_after = baseline_expected_rto
    expected_rto_avoided = 0.0
    intervention_cost = 0.0
    estimated_net_impact = 0.0
    converted_orders = 0.0

    if action == "WHATSAPP_CONFIRMATION":

        # Assumption: WhatsApp reduces each eligible order's
        # RTO probability by the configured relative percentage.
        expected_rto_after = (
            baseline_expected_rto * (1 - whatsapp_reduction)
        )

        expected_rto_avoided = (
            baseline_expected_rto - expected_rto_after
        )

        # WhatsApp service cost is not supplied, so excluded.
        estimated_net_impact = (
            expected_rto_avoided * rto_cost
        )

    elif action == "PREPAID_NUDGE":

        # Expected number of customers converting to prepaid.
        converted_orders = order_count * prepaid_conversion

        # Expected RTOs avoided among converted customers.
        expected_rto_avoided = (
            group["predicted_rto_probability"]
            .apply(
                lambda p: prepaid_conversion * max(
                    0, p - prepaid_rto
                )
            )
            .sum()
        )

        expected_rto_after = (
            baseline_expected_rto - expected_rto_avoided
        )

        intervention_cost = (
            converted_orders * prepaid_discount
        )

        estimated_net_impact = (
            expected_rto_avoided * rto_cost
            - intervention_cost
        )

    results.append({
        "action": action,
        "orders": order_count,
        "actual_historical_rto": actual_rto_count,
        "baseline_expected_rto": round(
            baseline_expected_rto, 2
        ),
        "expected_rto_after_intervention": round(
            expected_rto_after, 2
        ),
        "expected_rto_avoided": round(
            expected_rto_avoided, 2
        ),
        "expected_prepaid_conversions": round(
            converted_orders, 2
        ),
        "intervention_cost": round(
            intervention_cost, 2
        ),
        "estimated_net_impact": round(
            estimated_net_impact, 2
        )
    })

# --------------------------------------------------
# 5. DISPLAY RESULTS
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n===== INTERVENTION ECONOMICS =====")
print(results_df.to_string(index=False))

print("\n===== ASSUMPTIONS =====")
print(f"RTO cost per order: ₹{rto_cost:.2f}")
print(f"WhatsApp relative risk reduction: {whatsapp_reduction:.0%}")
print(f"Prepaid conversion rate: {prepaid_conversion:.0%}")
print(f"Prepaid RTO probability: {prepaid_rto:.0%}")
print(f"Prepaid discount per conversion: ₹{prepaid_discount:.2f}")

print("\n===== IMPORTANT LIMITATIONS =====")
print("These are simulated estimates, not measured intervention results.")
print("WhatsApp service costs are excluded.")
print("Prepaid payment gateway and other costs are excluded.")
print("Actual historical RTO counts are shown for comparison only.")
print("Expected RTOs are calculated from model probabilities.")

# --------------------------------------------------
# 6. SAVE RESULTS
# --------------------------------------------------

results_df.to_csv(OUTPUT_PATH, index=False)

print("\nResults saved to:")
print(OUTPUT_PATH)
