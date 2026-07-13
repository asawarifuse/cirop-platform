"""
Prefect ML Pipeline — Orchestrates segmentation, CLV, and churn prediction
"""

from prefect import flow, task
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"

@task(name="fetch-data", description="Fetch customer transactions from database")
def fetch_data():
    engine = create_engine(DB_URL)
    query = """
        SELECT t.customer_sk, t.order_date_sk::date as order_date, t.net_revenue as amount
        FROM fact_transactions t WHERE t.order_status = 'Completed'
    """
    df = pd.read_sql(query, engine)
    print(f"  Fetched {len(df)} transactions from {df['customer_sk'].nunique()} customers")
    return df

@task(name="run-segmentation", description="Segment customers using RFM analysis")
def run_segmentation(df):
    reference_date = datetime(2024, 12, 31)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    rfm = df.groupby('customer_sk').agg(
        recency=('order_date', lambda x: (reference_date - x.max()).days),
        frequency=('order_date', 'count'),
        monetary=('amount', 'sum')
    ).reset_index()
    
    rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    
    def assign_segment(r, f):
        r, f = int(r), int(f)
        if r >= 4 and f >= 4: return 'Champions'
        elif r >= 4 and f >= 2: return 'Loyal Customers'
        elif r >= 3 and f >= 3: return 'Potential Loyalists'
        elif r >= 3 and f <= 2: return 'At Risk'
        elif r <= 2: return 'Lost Customers'
        return 'Needs Attention'
    
    rfm['segment'] = rfm.apply(lambda x: assign_segment(x['r_score'], x['f_score']), axis=1)
    print(f"  Segmented {len(rfm)} customers into {rfm['segment'].nunique()} segments")
    return rfm

@task(name="write-segments", description="Write segments back to database")
def write_segments(rfm):
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        for _, row in rfm.iterrows():
            conn.execute(
                text("UPDATE dim_customer SET current_segment = :seg, updated_at = NOW() WHERE customer_sk = :sk"),
                {'seg': row['segment'], 'sk': int(row['customer_sk'])}
            )
        conn.commit()
    print(f"  Updated {len(rfm)} customers in database")

@flow(name="cirop-ml-pipeline", description="Complete ML pipeline for CIROP")
def ml_pipeline():
    print("=" * 50)
    print(f"CIROP ML Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    print("\n1. Fetching data...")
    df = fetch_data()
    
    print("\n2. Running segmentation...")
    rfm = run_segmentation(df)
    
    print("\n3. Writing results...")
    write_segments(rfm)
    
    # Summary
    counts = rfm['segment'].value_counts()
    print("\nSegment Distribution:")
    for seg, count in counts.items():
        print(f"  {seg}: {count} ({count/len(rfm)*100:.1f}%)")
    
    print("\nPipeline complete!")

if __name__ == "__main__":
    ml_pipeline()