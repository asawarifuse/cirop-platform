"""
Custom Data Drift Monitoring — Compares reference vs current data
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from scipy import stats

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== Data Drift Monitoring ===\n")

# 1. Fetch data
print("1. Fetching customer data...")
query = """
    SELECT 
        c.customer_sk,
        COUNT(t.transaction_sk) as total_orders,
        COALESCE(SUM(t.net_revenue), 0) as total_revenue,
        ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) as days_since_purchase
    FROM dim_customer c
    LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk AND t.order_status = 'Completed'
    GROUP BY c.customer_sk
"""
df = pd.read_sql(query, engine).fillna(0)
print(f"   Fetched {len(df)} customers")

# 2. Split reference (first 60%) and current (last 40%)
split = int(len(df) * 0.6)
ref = df.iloc[:split]
cur = df.iloc[split:]

print(f"   Reference: {len(ref)} | Current: {len(cur)}")

# 3. Compare distributions
print("\n2. Drift Analysis:")
print("-" * 55)
print(f"{'Feature':<22s} {'Ref Mean':>10s} {'Cur Mean':>10s} {'Change %':>8s} {'Drift':>8s}")
print("-" * 55)

drift_report = []

for col in ['total_orders', 'total_revenue', 'days_since_purchase']:
    ref_mean = ref[col].mean()
    cur_mean = cur[col].mean()
    change = ((cur_mean - ref_mean) / ref_mean * 100) if ref_mean != 0 else 0
    
    # KS test for distribution drift
    ks_stat, p_value = stats.ks_2samp(ref[col], cur[col])
    drifted = "YES" if p_value < 0.05 else "No"
    
    print(f"{col:<22s} ${ref_mean:>9,.2f} ${cur_mean:>9,.2f} {change:>7.1f}% {drifted:>8s}")
    
    drift_report.append({
        'feature': col,
        'reference_mean': round(ref_mean, 2),
        'current_mean': round(cur_mean, 2),
        'change_pct': round(change, 1),
        'p_value': round(p_value, 4),
        'drift_detected': drifted == "YES"
    })

# 4. Summary
drifts = [d for d in drift_report if d['drift_detected']]
print(f"\n3. Summary: {len(drifts)}/3 features show drift")

if drifts:
    print("   Drifted features:")
    for d in drifts:
        print(f"   - {d['feature']}: {d['change_pct']}% change (p={d['p_value']})")
else:
    print("   No significant drift detected — models are stable.")

# 5. Save report
report_df = pd.DataFrame(drift_report)
report_df.to_csv('data_drift_report.csv', index=False)
print("\n   Report saved to data_drift_report.csv")

print("\n=== Monitoring Complete ===")