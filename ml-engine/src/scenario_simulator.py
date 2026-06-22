"""
Scenario Simulator
Answers "what if" questions using real customer data
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== SCENARIO SIMULATOR ===\n")

# 1. Fetch customer data
print("1. Fetching customer data...")
query = """
    SELECT 
        c.customer_sk,
        c.current_segment,
        c.acquisition_channel,
        COUNT(t.transaction_sk) as total_orders,
        COALESCE(SUM(t.net_revenue), 0) as total_revenue,
        COALESCE(AVG(t.net_revenue), 0) as avg_order_value,
        ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) as days_since_purchase
    FROM dim_customer c
    LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk AND t.order_status = 'Completed'
    GROUP BY c.customer_sk, c.current_segment, c.acquisition_channel
"""
df = pd.read_sql(query, engine)
df['total_orders'] = df['total_orders'].fillna(0)
df['total_revenue'] = df['total_revenue'].fillna(0)
df['avg_order_value'] = df['avg_order_value'].fillna(0)
df['days_since_purchase'] = df['days_since_purchase'].fillna(999)
df['is_churned'] = (df['days_since_purchase'] > 90).astype(int)

print(f"   {len(df)} customers loaded")
print(f"   Total revenue: ${df['total_revenue'].sum():,.2f}")
print(f"   Churned: {df['is_churned'].sum()} ({df['is_churned'].mean()*100:.1f}%)")
print(f"   Avg AOV: ${df['avg_order_value'].mean():,.2f}")

# 2. Segment breakdown
print("\n2. Revenue by Segment:")
segments = df.groupby('current_segment').agg(
    customers=('customer_sk', 'count'),
    total_revenue=('total_revenue', 'sum'),
    avg_revenue=('total_revenue', 'mean'),
    churn_rate=('is_churned', 'mean')
).round(2)
print(segments.to_string())

# 3. Run Scenarios
print("\n3. Scenario Analysis")
print("=" * 55)

# Scenario 1: Reduce churn by 10%
print("\n📊 Scenario 1: What if churn decreases by 10%?")
current_churn = df['is_churned'].sum()
new_churn = int(current_churn * 0.9)
saved = current_churn - new_churn
churn_revenue = saved * df['total_revenue'].mean()
print(f"   Churned customers: {current_churn} → {new_churn}")
print(f"   Customers saved:   {saved}")
print(f"   Revenue impact:    ${churn_revenue:>12,.2f}")

# Scenario 2: Increase retention by 5%
print("\n📊 Scenario 2: What if retention increases by 5%?")
active = len(df) - current_churn
new_active = int(active * 1.05)
retained = new_active - active
retention_revenue = retained * df['total_revenue'].mean()
print(f"   Active customers:  {active} → {new_active}")
print(f"   Newly retained:    {retained}")
print(f"   Revenue impact:    ${retention_revenue:>12,.2f}")

# Scenario 3: Increase marketing budget by 20%
print("\n📊 Scenario 3: What if marketing budget increases by 20%?")
paid = df[df['acquisition_channel'] == 'Paid_Search']
paid_count = len(paid)
new_paid = int(paid_count * 1.2)
extra = new_paid - paid_count
paid_avg_rev = paid['total_revenue'].mean()
marketing_revenue = extra * paid_avg_rev
print(f"   Paid customers:    {paid_count} → {new_paid}")
print(f"   Additional:        {extra}")
print(f"   Revenue impact:    ${marketing_revenue:>12,.2f}")

# Scenario 4: Increase AOV by $50
print("\n📊 Scenario 4: What if avg order value increases by $50?")
total_orders = int(df['total_orders'].sum())
aov_increase = total_orders * 50
print(f"   Total orders:      {total_orders}")
print(f"   Current avg AOV:   ${df['avg_order_value'].mean():,.2f}")
print(f"   Revenue impact:    ${aov_increase:>12,.2f}")

# Scenario 5: Convert 20% of At Risk to Loyal
print("\n📊 Scenario 5: What if 20% of At Risk become Loyal?")
at_risk = df[df['current_segment'] == 'At Risk']
at_risk_count = len(at_risk)
converted = int(at_risk_count * 0.2)
loyal_avg = df[df['current_segment'] == 'Loyal Customers']['total_revenue'].mean()
at_risk_avg = at_risk['total_revenue'].mean()
uplift_per_customer = loyal_avg - at_risk_avg
conversion_revenue = converted * uplift_per_customer
print(f"   At Risk customers: {at_risk_count}")
print(f"   Converted:         {converted}")
print(f"   Revenue uplift/cust: ${uplift_per_customer:,.2f}")
print(f"   Revenue impact:    ${conversion_revenue:>12,.2f}")

# 4. Summary Table
print("\n4. Scenario Impact Summary")
print("=" * 55)
print(f"{'Scenario':<38s} {'Revenue Impact':>15s}")
print("-" * 55)
print(f"{'10% Churn Reduction':<38s} ${churn_revenue:>14,.2f}")
print(f"{'5% Retention Increase':<38s} ${retention_revenue:>14,.2f}")
print(f"{'20% Marketing Budget Increase':<38s} ${marketing_revenue:>14,.2f}")
print(f"{'$50 AOV Increase':<38s} ${aov_increase:>14,.2f}")
print(f"{'20% At Risk → Loyal Conversion':<38s} ${conversion_revenue:>14,.2f}")

# 5. Recommendation
print("\n5. Top Recommendation:")
impacts = {
    'Churn Reduction': churn_revenue,
    'Retention Increase': retention_revenue,
    'Marketing Budget': marketing_revenue,
    'AOV Increase': aov_increase,
    'At Risk Conversion': conversion_revenue
}
best = max(impacts, key=impacts.get)
print(f"   🏆 {best} delivers the highest ROI: ${impacts[best]:,.2f}")

print(f"\n=== SCENARIO SIMULATION COMPLETE ===")