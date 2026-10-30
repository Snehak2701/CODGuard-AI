
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. LOAD AND CLEAN DATA
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "data" / "orders_sample.csv"

df = pd.read_csv(FILE_PATH)

# Normalize status
df["final_status"] = (
    df["final_status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# Remove exact duplicate rows
df = df.drop_duplicates().copy()

# Keep completed orders only
df = df[
    df["final_status"].isin(["DELIVERED", "RTO"])
].copy()

# Create binary target column
# 1 = RTO, 0 = Delivered
df["is_rto"] = (
    df["final_status"] == "RTO"
).astype(int)

print("\n======================================")
print("       CODGUARD AI - EDA REPORT")
print("======================================")

# ==========================================
# 2. PREVIOUS RTO HISTORY
# ==========================================

print("\n1. RTO RATE BY PREVIOUS RTO HISTORY")

previous_rto = (
    df.groupby("customer_prior_rto")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("is_rto", "sum"),
        rto_rate=("is_rto", "mean")
    )
)

previous_rto["rto_rate"] *= 100

print(previous_rto.round(2))

# ==========================================
# 3. MARKETING SOURCE ANALYSIS
# ==========================================

print("\n2. RTO RATE BY MARKETING SOURCE")

marketing = (
    df.groupby("utm_source")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("is_rto", "sum"),
        rto_rate=("is_rto", "mean")
    )
)

marketing["rto_rate"] *= 100

print(marketing.sort_values(
    "rto_rate", ascending=False
).round(2))

# ==========================================
# 4. COURIER ANALYSIS
# ==========================================

print("\n3. RTO RATE BY COURIER")

courier = (
    df.groupby("courier")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("is_rto", "sum"),
        rto_rate=("is_rto", "mean")
    )
)

courier["rto_rate"] *= 100

print(courier.sort_values(
    "rto_rate", ascending=False
).round(2))

# ==========================================
# 5. STATE ANALYSIS
# ==========================================

print("\n4. RTO RATE BY STATE")

state = (
    df.groupby("state")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("is_rto", "sum"),
        rto_rate=("is_rto", "mean")
    )
)

state["rto_rate"] *= 100

print(state.sort_values(
    "rto_rate", ascending=False
).round(2))

# ==========================================
# 6. CUSTOMER ORDER HISTORY
# ==========================================

print("\n5. RTO RATE BY PREVIOUS ORDER COUNT")

history = (
    df.groupby("customer_prior_orders")
    .agg(
        total_orders=("order_id", "count"),
        rto_orders=("is_rto", "sum"),
        rto_rate=("is_rto", "mean")
    )
)

history["rto_rate"] *= 100

print(history.round(2))

# ==========================================
# 7. ADDRESS AND NAME QUALITY EXPLORATION
# ==========================================

suspicious_terms = [
    "test", "asdf", "xyz", "dummy", "unknown"
]

df["suspicious_name"] = df["customer_name"].fillna(
    ""
).str.lower().apply(
    lambda name: any(term in name for term in suspicious_terms)
)

suspicious_addresses = [
    ".", "xyz", "home", "call me", "asdf", "test"
]

df["weak_address"] = df["address"].fillna(
    ""
).str.lower().str.strip().apply(
    lambda address: any(
        term == address for term in suspicious_addresses
    )
)

print("\n6. NAME QUALITY ANALYSIS")

print(
    df.groupby("suspicious_name")["is_rto"]
    .agg(["count", "mean"])
    .rename(columns={"mean": "rto_rate"})
)

print("\n7. ADDRESS QUALITY ANALYSIS")

print(
    df.groupby("weak_address")["is_rto"]
    .agg(["count", "mean"])
    .rename(columns={"mean": "rto_rate"})
)

# ==========================================
# 8. ORDER VALUE ANALYSIS
# ==========================================

df["order_value_group"] = pd.cut(
    df["order_value"],
    bins=[0, 400, 650, 1000, float("inf")],
    labels=["Below 400", "400-650", "650-1000", "Above 1000"]
)

print("\n8. RTO RATE BY ORDER VALUE")

value_analysis = (
    df.groupby("order_value_group", observed=False)
    ["is_rto"]
    .agg(["count", "mean"])
)

value_analysis["mean"] *= 100

print(value_analysis.round(2))

# ==========================================
# 9. GENERATE GRAPHS
# ==========================================

GRAPH_DIR = BASE_DIR / "analysis" / "graphs"
GRAPH_DIR.mkdir(exist_ok=True)

charts = {
    "previous_rto": previous_rto["rto_rate"],
    "marketing_source": marketing["rto_rate"],
    "courier": courier["rto_rate"],
    "state": state["rto_rate"]
}

for chart_name, values in charts.items():

    plt.figure(figsize=(10, 5))

    values.sort_values().plot(kind="bar")

    plt.title(f"RTO Rate - {chart_name}")
    plt.xlabel(chart_name)
    plt.ylabel("RTO Rate (%)")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(GRAPH_DIR / f"{chart_name}.png")

    plt.close()

print("\nGraphs saved in:", GRAPH_DIR)

print("\n======================================")
print("             EDA COMPLETED")
print("======================================")
