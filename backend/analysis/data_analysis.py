import pandas as pd
from pathlib import Path

# --------------------------------
# 1. Load the dataset
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "data" / "orders_sample.csv"

df = pd.read_csv(FILE_PATH)

print("\n====================================")
print("       CODGUARD AI - DATA ANALYSIS")
print("====================================")

# --------------------------------
# 2. Display dataset information
# --------------------------------

print("\n1. DATASET INFORMATION")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

# --------------------------------
# 3. Check missing values
# --------------------------------

print("\n2. MISSING VALUES")

missing_values = df.isnull().sum()

print(missing_values[missing_values > 0])

# --------------------------------
# 4. Check duplicate records
# --------------------------------

print("\n3. DUPLICATE RECORDS")

print("Exact duplicate rows:", df.duplicated().sum())

print("Duplicate order IDs:", df["order_id"].duplicated().sum())

# --------------------------------
# 5. Normalize order status
# --------------------------------

df["final_status"] = (
    df["final_status"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print("\n4. ORDER STATUS DISTRIBUTION")

print(df["final_status"].value_counts(dropna=False))

# --------------------------------
# 6. Remove exact duplicate rows
# --------------------------------

df = df.drop_duplicates().copy()

print("\nRows after removing exact duplicates:", len(df))

# --------------------------------
# 7. Calculate delivered and RTO
# --------------------------------

delivered_orders = (df["final_status"] == "DELIVERED").sum()

rto_orders = (df["final_status"] == "RTO").sum()

pending_orders = len(df) - delivered_orders - rto_orders

completed_orders = delivered_orders + rto_orders

if completed_orders > 0:
    rto_percentage = (rto_orders / completed_orders) * 100
else:
    rto_percentage = 0

delivery_percentage = (
    (delivered_orders / completed_orders) * 100
    if completed_orders > 0 else 0
)

print("\n5. ORDER PERFORMANCE")

print("Delivered orders:", delivered_orders)
print("RTO orders:", rto_orders)
print("Pending/other orders:", pending_orders)

print("Completed orders:", completed_orders)

print(f"RTO percentage: {rto_percentage:.2f}%")
print(f"Delivery percentage: {delivery_percentage:.2f}%")

# --------------------------------
# 8. Calculate estimated RTO cost
# --------------------------------

shipping_cost = 65
return_shipping_cost = 65
packaging_cost = 25
damage_cost = 180 * 0.08

rto_cost_per_order = (
    shipping_cost
    + return_shipping_cost
    + packaging_cost
    + damage_cost
)

total_rto_cost = rto_orders * rto_cost_per_order

print("\n6. FINANCIAL ANALYSIS")

print(f"Expected cost per RTO: Rs. {rto_cost_per_order:.2f}")

print(f"Estimated total RTO cost: Rs. {total_rto_cost:.2f}")

# --------------------------------
# 9. Display sample records
# --------------------------------

print("\n7. FIRST FIVE ORDERS")

print(df.head().to_string(index=False))

print("\n====================================")
print("       ANALYSIS COMPLETED")
print("====================================")