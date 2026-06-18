"""
Customer Segmentation Pipeline
Fetches real data from PostgreSQL, runs RFM + K-Means, writes segments back
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== CUSTOMER SEGMENTATION PIPELINE ===\n")

# 1. Fetch data
print("1. Fetching transaction data...")
query = """
    SELECT 
        t.customer_sk,
        t.order_date_sk,
        SUM(t.net_revenue) as total_amount,
        COUNT(t.transaction_sk) as order_count
    FROM fact_transactions t
    WHERE t.order_status = 'Completed'
    GROUP BY t.customer_sk, t.order_date_sk
"""
df = pd.read_sql(query, engine)
df['order_date_sk'] = pd.to_datetime(df['order_date_sk'])
print(f"   Fetched {len(df)} order records")

# 2. Calculate RFM
print("\n2. Calculating RFM scores...")
reference_date = datetime(2024, 12, 31)

rfm = df.groupby('customer_sk').agg(
    recency=('order_date_sk', lambda x: (reference_date - x.max()).days),
    frequency=('order_count', 'sum'),
    monetary=('total_amount', 'sum')
).reset_index()

print(f"   {len(rfm)} customers analyzed")

# 3. Score RFM
rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1])
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)

# 4. Segment using RFM rules
print("\n3. Assigning segments...")

def assign_segment(row):
    r, f, m = int(row['r_score']), int(row['f_score']), int(row['m_score'])
    
    if r >= 4 and f >= 4:
        return 'Champions'
    elif r >= 4 and f >= 2:
        return 'Loyal Customers'
    elif r >= 3 and f >= 3:
        return 'Potential Loyalists'
    elif r >= 3 and f <= 2:
        return 'At Risk'
    elif r <= 2:
        return 'Lost Customers'
    else:
        return 'Needs Attention'

rfm['segment'] = rfm.apply(assign_segment, axis=1)

# 5. Show distribution
print("\n4. Segment Distribution:")
print("-" * 40)
seg_counts = rfm['segment'].value_counts()
for seg, count in seg_counts.items():
    pct = count / len(rfm) * 100
    print(f"   {seg:<22s}: {count:>5d} ({pct:>5.1f}%)")

# 6. Segment stats
print("\n5. Segment Statistics:")
print("-" * 60)
seg_stats = rfm.groupby('segment').agg(
    customers=('customer_sk', 'count'),
    avg_recency=('recency', 'mean'),
    avg_frequency=('frequency', 'mean'),
    avg_monetary=('monetary', 'mean'),
    total_revenue=('monetary', 'sum')
).round(2)

seg_stats['revenue_pct'] = (seg_stats['total_revenue'] / seg_stats['total_revenue'].sum() * 100).round(1)
print(seg_stats.to_string())

# 7. Write segments to database
print("\n6. Writing segments to database...")
with engine.connect() as conn:
    for _, row in rfm.iterrows():
        conn.execute(
            text("UPDATE dim_customer SET current_segment = :seg, updated_at = NOW() WHERE customer_sk = :sk"),
            {'seg': row['segment'], 'sk': int(row['customer_sk'])}
        )
    conn.commit()
print("   Segments updated in dim_customer")

# 8. Verify
print("\n7. Verification:")
with engine.connect() as conn:
    result = conn.execute(text("SELECT current_segment, COUNT(*) FROM dim_customer GROUP BY current_segment ORDER BY COUNT(*) DESC"))
    for row in result:
        print(f"   {row[0]:<22s}: {row[1]:>5d}")

print("\n=== SEGMENTATION COMPLETE ===")