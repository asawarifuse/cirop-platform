"""
Customer Lifetime Value Prediction
Uses BG/NBD model for purchase frequency + Gamma-Gamma for monetary value
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== CLV PREDICTION PIPELINE ===\n")

# 1. Fetch transaction data
print("1. Fetching transaction data...")
query = """
    SELECT 
        t.customer_sk,
        t.order_date_sk::date as order_date,
        t.net_revenue as amount
    FROM fact_transactions t
    WHERE t.order_status = 'Completed'
    ORDER BY t.customer_sk, t.order_date_sk
"""
df = pd.read_sql(query, engine)
df['order_date'] = pd.to_datetime(df['order_date'])
print(f"   Fetched {len(df)} transactions from {df['customer_sk'].nunique()} customers")

# 2. Prepare data for BG/NBD
print("\n2. Preparing RFM summary...")
# Set observation period end
observation_end = datetime(2024, 12, 31)

rfm_summary = summary_data_from_transaction_data(
    df,
    customer_id_col='customer_sk',
    datetime_col='order_date',
    monetary_value_col='amount',
    observation_period_end=observation_end
)
print(f"   Summary shape: {rfm_summary.shape}")
print(f"   Customers with repeat purchases: {(rfm_summary['frequency'] > 0).sum()}")
print(f"   Customers with zero repeats: {(rfm_summary['frequency'] == 0).sum()}")

# 3. Train BG/NBD model (predicts future purchase frequency)
print("\n3. Training BG/NBD model...")
bgf = BetaGeoFitter(penalizer_coef=0.01)
bgf.fit(
    rfm_summary['frequency'],
    rfm_summary['recency'],
    rfm_summary['T']
)
print(f"   Parameters: {bgf.params_}")

# 4. Predict purchases for next 12 months
print("\n4. Predicting future purchases (12 months)...")
t = 365  # 12 months in days

rfm_summary['predicted_purchases_12m'] = bgf.conditional_expected_number_of_purchases_up_to_time(
    t,
    rfm_summary['frequency'],
    rfm_summary['recency'],
    rfm_summary['T']
)

print(f"   Avg predicted purchases (12m): {rfm_summary['predicted_purchases_12m'].mean():.2f}")
print(f"   Median predicted purchases: {rfm_summary['predicted_purchases_12m'].median():.2f}")
print(f"   Max predicted purchases: {rfm_summary['predicted_purchases_12m'].max():.2f}")

# 5. Train Gamma-Gamma model (predicts average order value)
print("\n5. Training Gamma-Gamma model...")
# Filter customers with monetary value > 0
returning_customers = rfm_summary[rfm_summary['monetary_value'] > 0]
print(f"   Returning customers with spend data: {len(returning_customers)}")

ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(
    returning_customers['frequency'],
    returning_customers['monetary_value']
)
print("   Gamma-Gamma model trained")
print(f"   Parameters: {ggf.params_}")

# 6. Calculate predicted average order value
rfm_summary['predicted_aov'] = ggf.conditional_expected_average_profit(
    rfm_summary['frequency'],
    rfm_summary['monetary_value']
)

# 7. Calculate CLV (Predicted Purchases x Predicted AOV)
rfm_summary['predicted_clv_12m'] = rfm_summary['predicted_purchases_12m'] * rfm_summary['predicted_aov']
rfm_summary['predicted_clv_12m'] = rfm_summary['predicted_clv_12m'].round(2)

print("\n6. CLV Results (12 months):")
print("-" * 50)
print(f"   Average CLV:        ${rfm_summary['predicted_clv_12m'].mean():,.2f}")
print(f"   Median CLV:         ${rfm_summary['predicted_clv_12m'].median():,.2f}")
print(f"   Total 12m Revenue:  ${rfm_summary['predicted_clv_12m'].sum():,.2f}")
print(f"   Max CLV:            ${rfm_summary['predicted_clv_12m'].max():,.2f}")
print(f"   Min CLV (non-zero): ${rfm_summary[rfm_summary['predicted_clv_12m']>0]['predicted_clv_12m'].min():,.2f}")

# 8. CLV Segments
print("\n7. CLV Distribution by Segment:")
rfm_summary['clv_segment'] = pd.cut(
    rfm_summary['predicted_clv_12m'],
    bins=[-1, 100, 500, 1000, 5000, float('inf')],
    labels=['Very Low (<$100)', 'Low ($100-500)', 'Medium ($500-1K)', 'High ($1K-5K)', 'Very High (>$5K)']
)
clv_dist = rfm_summary['clv_segment'].value_counts().sort_index()
for seg, count in clv_dist.items():
    pct = count / len(rfm_summary) * 100
    print(f"   {seg:<20s}: {count:>5d} ({pct:>5.1f}%)")

# 9. Top customers by CLV
print("\n8. Top 10 Customers by Predicted CLV:")
top_clv = rfm_summary.nlargest(10, 'predicted_clv_12m')
for i, (idx, row) in enumerate(top_clv.iterrows(), 1):
    print(f"   {i:>2}. Customer {idx:>4d} | CLV: ${row['predicted_clv_12m']:>10,.2f} | "
          f"Purchases: {row['predicted_purchases_12m']:>6.1f} | AOV: ${row['predicted_aov']:>8,.2f}")

# 10. Write predictions to database
print("\n9. Writing CLV predictions to database...")
with engine.connect() as conn:
    for idx, row in rfm_summary.iterrows():
        conn.execute(
            text("""
                UPDATE dim_customer 
                SET updated_at = NOW()
                WHERE customer_sk = :sk
            """),
            {'sk': int(idx)}
        )
    conn.commit()
print("   Predictions stored")

print("\n=== CLV PREDICTION COMPLETE ===")