
import pandas as pd
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score

# --------------------------------------------------
# 1. LOAD TIME-BASED TEST RESULTS
# --------------------------------------------------

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent

INPUT_PATH = (
    BACKEND_DIR / "data" / "time_based_test_results.csv"
)

OUTPUT_PATH = (
    BACKEND_DIR / "data" / "threshold_analysis.csv"
)

df = pd.read_csv(INPUT_PATH)

y_true = df["is_rto"].astype(int)
y_prob = df["predicted_rto_probability"]

# --------------------------------------------------
# 2. BUSINESS FINANCIAL ASSUMPTIONS
# --------------------------------------------------

forward_shipping = 65
return_shipping = 65
packaging_handling = 25
expected_damage = 180 * 0.08

rto_cost = (
    forward_shipping
    + return_shipping
    + packaging_handling
    + expected_damage
)

delivered_gross_profit = 649 * 0.62

# Assumption: forward shipping is separate from gross margin
delivered_contribution = delivered_gross_profit - forward_shipping

# --------------------------------------------------
# 3. TEST DIFFERENT THRESHOLDS
# --------------------------------------------------

thresholds = [
    0.20, 0.30, 0.40, 0.50, 0.60,
    0.6657, 0.70, 0.80
]

results = []

for threshold in thresholds:

    # Orders above threshold are flagged for intervention
    y_pred = (y_prob >= threshold).astype(int)

    true_positive = int(((y_pred == 1) & (y_true == 1)).sum())
    false_positive = int(((y_pred == 1) & (y_true == 0)).sum())
    false_negative = int(((y_pred == 0) & (y_true == 1)).sum())
    true_negative = int(((y_pred == 0) & (y_true == 0)).sum())

    flagged_orders = true_positive + false_positive

    precision = precision_score(
        y_true, y_pred, zero_division=0
    )

    recall = recall_score(
        y_true, y_pred, zero_division=0
    )

    f1 = f1_score(
        y_true, y_pred, zero_division=0
    )

    # Historical counterfactual:
    # What if all flagged orders had been cancelled?
    avoided_rto_cost = true_positive * rto_cost

    lost_delivered_contribution = (
        false_positive * delivered_contribution
    )

    net_impact = (
        avoided_rto_cost - lost_delivered_contribution
    )

    results.append({
        "threshold": threshold,
        "flagged_orders": flagged_orders,
        "true_rto_identified": true_positive,
        "genuine_orders_flagged": false_positive,
        "missed_rto_orders": false_negative,
        "correctly_unflagged_delivered": true_negative,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "potential_rto_cost_avoided": round(
            avoided_rto_cost, 2
        ),
        "potential_genuine_contribution_lost": round(
            lost_delivered_contribution, 2
        ),
        "hypothetical_net_impact": round(net_impact, 2)
    })


# --------------------------------------------------
# 4. DISPLAY RESULTS
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n===== THRESHOLD ANALYSIS =====")

print(
    results_df.to_string(
        index=False
    )
)

print("\n===== BUSINESS ASSUMPTIONS =====")
print(f"RTO cost: ₹{rto_cost:.2f}")
print(f"Delivered contribution: ₹{delivered_contribution:.2f}")

print("\nIMPORTANT:")
print(
    "Financial impact is a historical counterfactual, "
    "assuming every flagged order was cancelled."
)
print(
    "It is not actual savings and does not include "
    "customer lifetime value or intervention costs."
)

# --------------------------------------------------
# 5. SAVE RESULTS
# --------------------------------------------------

results_df.to_csv(OUTPUT_PATH, index=False)

print("\nAnalysis saved to:")
print(OUTPUT_PATH)
