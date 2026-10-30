
import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="CODGuard AI Dashboard",
    page_icon="📦",
    layout="wide"
)

st.title("📦 CODGuard AI")
st.subheader("Founder Dashboard")
st.caption("Historical order analysis and ML-based RTO risk monitoring")

# -----------------------------
# LOAD DATA AND MODEL
# -----------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "backend" / "data" / "orders_sample.csv"
MODEL_PATH = ROOT_DIR / "backend" / "models" / "codguard_model.pkl"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Remove exact duplicate rows
    df = df.drop_duplicates().copy()

    # Normalize order status
    df["final_status"] = (
        df["final_status"].astype(str).str.strip().str.upper()
    )

    # Exclude orders whose final outcome is not known
    df = df[df["final_status"].isin(["DELIVERED", "RTO"])].copy()

    df["order_datetime"] = pd.to_datetime(
        df["order_datetime"], errors="coerce"
    )

    return df


@st.cache_resource
def load_model():
    saved_model = joblib.load(MODEL_PATH)
    return saved_model["model"]


df = load_data()
model = load_model()

# -----------------------------
# PREDICT RTO RISK
# -----------------------------

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

df["risk_bucket"] = pd.cut(
    df["predicted_rto_probability"],
    bins=[-0.001, 0.20, 0.40, 0.65, 1.0],
    labels=["Low", "Moderate", "High", "Very High"]
)

# -----------------------------
# CODGUARD DECISION BUCKETS
# -----------------------------

def assign_action(row):

    risk = row["predicted_rto_probability"]

    if risk < 0.20:
        return "SHIP_AS_IS"

    elif risk < 0.40:
        return "CONFIRM_ON_WHATSAPP"

    elif risk < 0.65:
        return "NUDGE_TO_PREPAID"

    else:
        return "HOLD_FOR_REVIEW"


df["decision_action"] = df.apply(assign_action, axis=1)

# Count orders in each decision bucket
decision_counts = (
    df["decision_action"]
    .value_counts()
    .reindex(
        [
            "SHIP_AS_IS",
            "CONFIRM_ON_WHATSAPP",
            "NUDGE_TO_PREPAID",
            "HOLD_FOR_REVIEW"
        ],
        fill_value=0
    )
)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.header("Dashboard Filters")

states = sorted(df["state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State",
    states,
    default=states
)

filtered_df = df[df["state"].isin(selected_states)].copy()

# -----------------------------
# KEY METRICS
# -----------------------------

total_orders = len(filtered_df)
total_rto = (filtered_df["final_status"] == "RTO").sum()
total_delivered = (filtered_df["final_status"] == "DELIVERED").sum()

rto_rate = (
    total_rto / total_orders * 100 if total_orders else 0
)

st.caption(
    f"Dataset snapshot: {filtered_df['order_datetime'].min():%d %b %Y}"
    f" – {filtered_df['order_datetime'].max():%d %b %Y}"
    if total_orders else "No orders in selected filters"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", f"{total_orders:,}")
col2.metric("Delivered Orders", f"{total_delivered:,}")
col3.metric("RTO Orders", f"{total_rto:,}")
col4.metric("Actual RTO Rate", f"{rto_rate:.2f}%")

st.divider()

# -----------------------------
# CODGUARD DECISION BUCKETS
# -----------------------------

st.subheader("CODGuard AI - Decision Distribution")

filtered_decisions = (
    filtered_df["decision_action"].value_counts()
)

ship_count = filtered_decisions.get("SHIP_AS_IS", 0)

confirm_count = filtered_decisions.get(
    "CONFIRM_ON_WHATSAPP", 0
)

prepaid_count = filtered_decisions.get(
    "NUDGE_TO_PREPAID", 0
)

hold_count = filtered_decisions.get(
    "HOLD_FOR_REVIEW", 0
)

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

# -----------------------------
# FINANCIAL IMPACT SIMULATOR
# -----------------------------

st.divider()
st.subheader("Financial Impact Analysis")

st.caption(
    "Scenario estimates based on configurable assumptions. "
    "These are not measured or realized savings."
)

# Assignment business assumptions
RTO_COST = 169.40
DELIVERED_GROSS_PROFIT = 402.38
PREPAID_DISCOUNT = 20

# Founder can adjust intervention assumptions
st.markdown("### Business assumptions")

col1, col2, col3 = st.columns(3)

with col1:
    intervention_success = st.slider(
        "Confirmation/prepaid intervention success (%)",
        min_value=0,
        max_value=100,
        value=30
    )

with col2:
    manual_cancel_rate = st.slider(
        "Genuine hold orders incorrectly cancelled (%)",
        min_value=0,
        max_value=100,
        value=10
    )

with col3:
    prepaid_conversion = st.slider(
        "Prepaid nudge conversion (%)",
        min_value=0,
        max_value=100,
        value=25
    )

# Count actionable orders
confirmation_orders = (
    filtered_df["decision_action"] == "CONFIRM_ON_WHATSAPP"
).sum()

prepaid_orders = (
    filtered_df["decision_action"] == "NUDGE_TO_PREPAID"
).sum()

hold_orders = (
    filtered_df["decision_action"] == "HOLD_FOR_REVIEW"
).sum()

# Average predicted risk for each group
confirmation_risk = filtered_df.loc[
    filtered_df["decision_action"] == "CONFIRM_ON_WHATSAPP",
    "predicted_rto_probability"
].mean()

prepaid_risk = filtered_df.loc[
    filtered_df["decision_action"] == "NUDGE_TO_PREPAID",
    "predicted_rto_probability"
].mean()

hold_risk = filtered_df.loc[
    filtered_df["decision_action"] == "HOLD_FOR_REVIEW",
    "predicted_rto_probability"
].mean()

# Handle empty groups
confirmation_risk = (
    0 if pd.isna(confirmation_risk) else confirmation_risk
)

prepaid_risk = (
    0 if pd.isna(prepaid_risk) else prepaid_risk
)

hold_risk = (
    0 if pd.isna(hold_risk) else hold_risk
)

# Estimated RTOs avoided by successful interventions
confirmation_saves = (
    confirmation_orders
    * confirmation_risk
    * intervention_success / 100
)

prepaid_saves = (
    prepaid_orders
    * prepaid_risk
    * prepaid_conversion / 100
)

estimated_rtos_avoided = confirmation_saves + prepaid_saves

estimated_rto_savings = estimated_rtos_avoided * RTO_COST

# Estimated genuine orders incorrectly cancelled
estimated_genuine_lost = (
    hold_orders
    * (1 - hold_risk)
    * manual_cancel_rate / 100
)

estimated_lost_profit = (
    estimated_genuine_lost * DELIVERED_GROSS_PROFIT
)

# Estimated prepaid discount expenditure
estimated_discount_cost = (
    prepaid_orders
    * prepaid_conversion / 100
    * PREPAID_DISCOUNT
)

# Net estimated impact
net_impact = (
    estimated_rto_savings
    - estimated_lost_profit
    - estimated_discount_cost
)

# Display financial metrics
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
    "Estimated Lost Gross Profit",
    f"₹{estimated_lost_profit:,.2f}"
)

col5, col6 = st.columns(2)

col5.metric(
    "Prepaid Discount Cost",
    f"₹{estimated_discount_cost:,.2f}"
)

col6.metric(
    "Estimated Net Impact",
    f"₹{net_impact:,.2f}"
)

st.caption(
    "Formula: RTO savings − lost delivered gross profit − prepaid "
    "discount expenditure. Estimates assume the selected intervention "
    "success rates apply to predicted risk. Validate these assumptions "
    "through a controlled experiment before claiming realized impact."
)

# -----------------------------
# RTO RISK DISTRIBUTION
# -----------------------------

st.subheader("Predicted RTO Risk Distribution")

risk_counts = (
    filtered_df["risk_bucket"]
    .value_counts()
    .reindex(["Low", "Moderate", "High", "Very High"], fill_value=0)
)

st.bar_chart(risk_counts)

# -----------------------------
# ACTUAL ORDER OUTCOMES
# -----------------------------

st.subheader("Actual Order Outcomes")

outcome_counts = filtered_df["final_status"].value_counts()

st.bar_chart(outcome_counts)

# -----------------------------
# MONTHLY RTO TREND
# -----------------------------

st.subheader("Monthly RTO Trend")

monthly = filtered_df.copy()

monthly["month"] = (
    monthly["order_datetime"].dt.to_period("M").astype(str)
)

monthly_summary = (
    monthly.groupby("month")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("final_status", lambda x: (x == "RTO").sum())
    )
)

monthly_summary["rto_rate"] = (
    monthly_summary["rto_orders"] /
    monthly_summary["total_orders"] * 100
)

st.line_chart(monthly_summary["rto_rate"])

# -----------------------------
# FINANCIAL OVERVIEW
# -----------------------------

st.subheader("Estimated RTO Cost")

RTO_COST = 169.40

estimated_rto_cost = total_rto * RTO_COST

col1, col2 = st.columns(2)

col1.metric(
    "Estimated Direct RTO Cost",
    f"₹{estimated_rto_cost:,.2f}"
)

col2.metric(
    "Direct Cost per RTO",
    f"₹{RTO_COST:,.2f}"
)

st.caption(
    "Estimated historical direct RTO cost using the assignment's "
    "₹169.40 cost assumption. This is not verified realized savings."
)

# -----------------------------
# ORDER TABLE
# -----------------------------

st.subheader("Order-Level Risk Details")

display_columns = [
    "order_id",
    "order_datetime",
    "city",
    "state",
    "order_value",
    "final_status",
    "predicted_rto_probability",
    "risk_bucket"
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

st.success("CODGuard AI dashboard loaded successfully!")
