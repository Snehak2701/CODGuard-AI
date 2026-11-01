
import streamlit as st
import pandas as pd
import joblib
import json
from pathlib import Path


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CODGuard AI Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 CODGuard AI")
st.subheader("Founder Dashboard")
st.caption(
    "Historical order analysis, ML-based RTO risk monitoring "
    "and financial decision support"
)


# --------------------------------------------------
# 2. LOAD CONFIGURATION, DATA AND MODEL
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT_DIR / "backend" / "data" / "orders_sample.csv"
MODEL_PATH = ROOT_DIR / "backend" / "models" / "codguard_model.pkl"
CONFIG_PATH = ROOT_DIR / "backend" / "config.json"


@st.cache_data
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


@st.cache_data
def load_data():
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

    return df


@st.cache_resource
def load_model():
    saved_model = joblib.load(MODEL_PATH)
    return saved_model["model"]


config = load_config()
df = load_data()
model = load_model()

THRESHOLDS = config["risk_thresholds"]
FINANCIAL = config["financial_assumptions"]
INTERVENTIONS = config["interventions"]


# --------------------------------------------------
# 3. FINANCIAL ASSUMPTIONS
# --------------------------------------------------

forward_cost = FINANCIAL["forward_shipping_cost"]
return_cost = FINANCIAL["return_shipping_cost"]
packaging_cost = FINANCIAL["packaging_handling_cost"]

damage_cost = (
    FINANCIAL["product_cost"]
    * FINANCIAL["damage_probability"]
)

rto_cost = (
    forward_cost
    + return_cost
    + packaging_cost
    + damage_cost
)

gross_profit = FINANCIAL["delivered_gross_profit"]

if FINANCIAL["delivered_gross_profit_includes_forward_shipping"]:
    delivered_contribution = gross_profit
else:
    delivered_contribution = gross_profit - forward_cost

prepaid_rto = FINANCIAL["prepaid_rto_probability"]
prepaid_discount = INTERVENTIONS["prepaid_discount"]
manual_review_cost = INTERVENTIONS["manual_review_cost_per_order"]


# --------------------------------------------------
# 4. PREDICT RTO RISK
# --------------------------------------------------

features = [
    "order_value",
    "customer_prior_orders",
    "customer_prior_rto",
    "state",
    "city",
    "courier",
    "utm_source"
]

df["predicted_rto_probability"] = model.predict_proba(
    df[features]
)[:, 1]


# --------------------------------------------------
# 5. ASSIGN RISK BUCKETS
# --------------------------------------------------

risk_bins = [
    0,
    THRESHOLDS["ship_as_is"],
    THRESHOLDS["whatsapp_confirmation"],
    THRESHOLDS["prepaid_nudge"],
    THRESHOLDS["manual_review"],
    1.000001
]

risk_labels = [
    "Low",
    "Moderate",
    "High",
    "Very High",
    "Critical"
]

df["risk_bucket"] = pd.cut(
    df["predicted_rto_probability"],
    bins=risk_bins,
    labels=risk_labels,
    right=False
)


# --------------------------------------------------
# 6. ASSIGN CODGUARD ACTIONS
# --------------------------------------------------

def assign_action(row):

    risk = row["predicted_rto_probability"]

    if risk < THRESHOLDS["ship_as_is"]:
        return "SHIP_AS_IS"

    elif risk < THRESHOLDS["whatsapp_confirmation"]:
        return "CONFIRM_ON_WHATSAPP"

    elif risk < THRESHOLDS["prepaid_nudge"]:
        return "NUDGE_TO_PREPAID"

    else:
        return "HOLD_FOR_REVIEW"


df["decision_action"] = df.apply(assign_action, axis=1)


# --------------------------------------------------
# 7. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

states = sorted(df["state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State",
    states,
    default=states
)

filtered_df = df[
    df["state"].isin(selected_states)
].copy()


# --------------------------------------------------
# 8. KEY BUSINESS METRICS
# --------------------------------------------------

total_orders = len(filtered_df)

total_rto = (
    filtered_df["final_status"] == "RTO"
).sum()

total_delivered = (
    filtered_df["final_status"] == "DELIVERED"
).sum()

rto_rate = (
    total_rto / total_orders * 100
    if total_orders else 0
)

if total_orders:
    min_date = filtered_df["order_datetime"].min()
    max_date = filtered_df["order_datetime"].max()

    st.caption(
        f"Historical dataset: {min_date:%d %b %Y}"
        f" – {max_date:%d %b %Y}"
    )

st.caption(
    "This dashboard uses historical sample data, not live Shopify "
    "orders or live yesterday's operational data."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Delivered Orders", f"{total_delivered:,}")
col3.metric("RTO Orders", f"{total_rto:,}")
col4.metric("Actual RTO Rate", f"{rto_rate:.2f}%")

st.divider()


# --------------------------------------------------
# 9. CODGUARD DECISION DISTRIBUTION
# --------------------------------------------------

st.subheader("CODGuard AI - Decision Distribution")

action_order = [
    "SHIP_AS_IS",
    "CONFIRM_ON_WHATSAPP",
    "NUDGE_TO_PREPAID",
    "HOLD_FOR_REVIEW"
]

decision_counts = (
    filtered_df["decision_action"]
    .value_counts()
    .reindex(action_order, fill_value=0)
)

ship_count = decision_counts["SHIP_AS_IS"]
confirm_count = decision_counts["CONFIRM_ON_WHATSAPP"]
prepaid_count = decision_counts["NUDGE_TO_PREPAID"]
hold_count = decision_counts["HOLD_FOR_REVIEW"]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ship As-Is", f"{ship_count:,}")
col2.metric("WhatsApp Confirmation", f"{confirm_count:,}")
col3.metric("Prepaid Nudge", f"{prepaid_count:,}")
col4.metric("Hold for Review", f"{hold_count:,}")

decision_chart = pd.Series({
    "Ship As-Is": ship_count,
    "WhatsApp Confirmation": confirm_count,
    "Prepaid Nudge": prepaid_count,
    "Hold for Review": hold_count
})

st.bar_chart(decision_chart)

st.caption(
    "Decision thresholds are loaded from backend/config.json. "
    "Orders in the 60–70% and 70%+ bands are both held for review."
)


# --------------------------------------------------
# 10. FINANCIAL IMPACT SIMULATOR
# --------------------------------------------------

st.divider()
st.subheader("Financial Impact Simulator")

st.caption(
    "Illustrative scenario estimates using the assignment's "
    "business assumptions. These are not actual or guaranteed savings."
)

st.markdown("### Adjustable intervention assumptions")

col1, col2, col3 = st.columns(3)

with col1:
    intervention_success = st.slider(
        "WhatsApp confirmation risk reduction (%)",
        min_value=0,
        max_value=100,
        value=int(
            INTERVENTIONS["whatsapp_confirmation_success_rate"] * 100
        )
    )

with col2:
    prepaid_conversion = st.slider(
        "Prepaid conversion rate (%)",
        min_value=0,
        max_value=100,
        value=int(
            INTERVENTIONS["prepaid_conversion_rate"] * 100
        )
    )

with col3:
    manual_cancel_rate = st.slider(
        "Held orders eventually cancelled after review (%)",
        min_value=0,
        max_value=100,
        value=10
    )


# Count intervention groups
confirmation_df = filtered_df[
    filtered_df["decision_action"] == "CONFIRM_ON_WHATSAPP"
]

prepaid_df = filtered_df[
    filtered_df["decision_action"] == "NUDGE_TO_PREPAID"
]

hold_df = filtered_df[
    filtered_df["decision_action"] == "HOLD_FOR_REVIEW"
]

confirmation_orders = len(confirmation_df)
prepaid_orders = len(prepaid_df)
hold_orders = len(hold_df)


# Average predicted risk in each group
confirmation_risk = (
    confirmation_df["predicted_rto_probability"].mean()
)

prepaid_risk = (
    prepaid_df["predicted_rto_probability"].mean()
)

hold_risk = (
    hold_df["predicted_rto_probability"].mean()
)

confirmation_risk = (
    0 if pd.isna(confirmation_risk) else confirmation_risk
)

prepaid_risk = (
    0 if pd.isna(prepaid_risk) else prepaid_risk
)

hold_risk = (
    0 if pd.isna(hold_risk) else hold_risk
)


# Estimated RTOs avoided through confirmation
confirmation_saves = (
    confirmation_orders
    * confirmation_risk
    * intervention_success / 100
)


# Prepaid savings must account for the residual prepaid RTO rate
prepaid_risk_reduction = max(
    0,
    prepaid_risk - prepaid_rto
)

prepaid_saves = (
    prepaid_orders
    * prepaid_risk_reduction
    * prepaid_conversion / 100
)


estimated_rtos_avoided = (
    confirmation_saves + prepaid_saves
)

estimated_rto_savings = (
    estimated_rtos_avoided * rto_cost
)


# Hypothetical genuine orders cancelled after manual review
estimated_genuine_lost = (
    hold_orders
    * (1 - hold_risk)
    * manual_cancel_rate / 100
)

estimated_lost_contribution = (
    estimated_genuine_lost * delivered_contribution
)


# Prepaid discount expense
estimated_discount_cost = (
    prepaid_orders
    * prepaid_conversion / 100
    * prepaid_discount
)


# Manual review expense
estimated_review_cost = (
    hold_orders * manual_review_cost
)


# Net estimated impact
net_impact = (
    estimated_rto_savings
    - estimated_lost_contribution
    - estimated_discount_cost
    - estimated_review_cost
)


# Display financial impact
st.markdown("### Estimated business impact")

col1, col2 = st.columns(2)

col1.metric(
    "Estimated RTOs Avoided",
    f"{estimated_rtos_avoided:.1f}"
)

col2.metric(
    "Estimated RTO Savings",
    f"₹{estimated_rto_savings:,.2f}"
)

col3, col4 = st.columns(2)

col3.metric(
    "Estimated Genuine Orders Lost",
    f"{estimated_genuine_lost:.1f}"
)

col4.metric(
    "Estimated Lost Contribution",
    f"₹{estimated_lost_contribution:,.2f}"
)

col5, col6 = st.columns(2)

col5.metric(
    "Prepaid Discount Cost",
    f"₹{estimated_discount_cost:,.2f}"
)

col6.metric(
    "Manual Review Cost",
    f"₹{estimated_review_cost:,.2f}"
)

st.metric(
    "Estimated Net Financial Impact",
    f"₹{net_impact:,.2f}"
)

st.caption(
    "Formula: estimated RTO savings − lost delivered contribution "
    "− prepaid discounts − manual review cost. The cancellation "
    "slider represents a hypothetical human decision after review, "
    "not automatic cancellation by CODGuard."
)

st.caption(
    f"Financial assumptions: delivered contribution ₹{delivered_contribution:.2f}, "
    f"RTO cost ₹{rto_cost:.2f}, prepaid RTO rate {prepaid_rto:.0%}, "
    f"prepaid discount ₹{prepaid_discount:.2f}."
)


# --------------------------------------------------
# 11. RTO RISK DISTRIBUTION
# --------------------------------------------------

st.divider()
st.subheader("Predicted RTO Risk Distribution")

risk_counts = (
    filtered_df["risk_bucket"]
    .value_counts()
    .reindex(risk_labels, fill_value=0)
)

st.bar_chart(risk_counts)


# --------------------------------------------------
# 12. ACTUAL ORDER OUTCOMES
# --------------------------------------------------

st.subheader("Actual Order Outcomes")

outcome_counts = filtered_df["final_status"].value_counts()

st.bar_chart(outcome_counts)


# --------------------------------------------------
# 13. MONTHLY RTO TREND
# --------------------------------------------------

st.subheader("Monthly RTO Trend")

monthly = filtered_df.dropna(
    subset=["order_datetime"]
).copy()

monthly["month"] = (
    monthly["order_datetime"].dt.to_period("M").astype(str)
)

monthly_summary = (
    monthly.groupby("month")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=(
            "final_status",
            lambda x: (x == "RTO").sum()
        )
    )
)

monthly_summary["rto_rate"] = (
    monthly_summary["rto_orders"]
    / monthly_summary["total_orders"] * 100
)

st.line_chart(monthly_summary["rto_rate"])


# --------------------------------------------------
# 14. HISTORICAL RTO COST
# --------------------------------------------------

st.divider()
st.subheader("Historical RTO Cost")

estimated_historical_rto_cost = total_rto * rto_cost

col1, col2 = st.columns(2)

col1.metric(
    "Estimated Direct RTO Cost",
    f"₹{estimated_historical_rto_cost:,.2f}"
)

col2.metric(
    "Estimated Direct Cost per RTO",
    f"₹{rto_cost:,.2f}"
)

st.caption(
    "Historical direct cost is calculated using the configured "
    "₹169.40 RTO cost assumption. It is not measured realized savings."
)


# --------------------------------------------------
# 15. ORDER-LEVEL DETAILS
# --------------------------------------------------

st.divider()
st.subheader("Order-Level Risk Details")

display_columns = [
    "order_id",
    "order_datetime",
    "city",
    "state",
    "order_value",
    "final_status",
    "predicted_rto_probability",
    "risk_bucket",
    "decision_action"
]

display_df = filtered_df[display_columns].copy()

display_df["predicted_rto_probability"] = (
    display_df["predicted_rto_probability"] * 100
).round(2)

st.dataframe(
    display_df.sort_values(
        "predicted_rto_probability",
        ascending=False
    ),
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# 16. FOOTER
# --------------------------------------------------

st.success("CODGuard AI dashboard loaded successfully!")

st.caption(
    "Note: Historical predictions are retrospective model estimates. "
    "The model's predictive performance and intervention assumptions "
    "should be validated before operational deployment."
)
