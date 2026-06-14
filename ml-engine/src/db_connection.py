"""
Database Connection Module
Connects Python ML Engine to PostgreSQL Analytics Database
"""

import pandas as pd
from sqlalchemy import create_engine
import os

DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'cirop_analytics',
    'user': 'cirop_user',
    'password': 'cirop_pass_2024'
}

def get_engine():
    """Create SQLAlchemy engine for PostgreSQL."""
    url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(url)


def fetch_customers(engine):
    """Fetch all customers from dim_customer."""
    query = "SELECT * FROM dim_customer"
    return pd.read_sql(query, engine)


def fetch_transactions(engine):
    """Fetch all transactions from fact_transactions."""
    query = """
        SELECT 
            t.transaction_bk,
            t.customer_sk,
            t.product_sk,
            t.order_date_sk as order_date,
            t.quantity,
            t.unit_price,
            t.net_revenue,
            t.order_status
        FROM fact_transactions t
    """
    return pd.read_sql(query, engine)


def fetch_customer_snapshots(engine):
    """Fetch customer snapshots for ML training."""
    query = """
        SELECT 
            s.customer_sk,
            s.snapshot_month_sk,
            s.recency_days,
            s.frequency,
            s.monetary_value,
            s.segment,
            s.predicted_clv_12m,
            s.churn_probability
        FROM fact_customer_snapshot s
        ORDER BY s.snapshot_month_sk DESC
    """
    return pd.read_sql(query, engine)


def write_segments(engine, df):
    """Write customer segments back to database."""
    for _, row in df.iterrows():
        query = f"""
            UPDATE dim_customer 
            SET current_segment = '{row['segment']}',
                updated_at = NOW()
            WHERE customer_sk = {row['customer_sk']}
        """
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()


def write_predictions(engine, df):
    """Write ML predictions to customer snapshot table."""
    for _, row in df.iterrows():
        query = f"""
            UPDATE fact_customer_snapshot 
            SET segment = '{row.get('segment', 'Unknown')}',
                predicted_clv_12m = {row.get('predicted_clv_12m', 0)},
                churn_probability = {row.get('churn_probability', 0)}
            WHERE customer_sk = {row['customer_sk']}
            AND snapshot_month_sk = '{row.get('snapshot_month_sk', '2024-06-01')}'
        """
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()


if __name__ == "__main__":
    engine = get_engine()
    
    try:
        # Test connection
        customers = fetch_customers(engine)
        print(f"Connected to database. Found {len(customers)} customers.")
        
        transactions = fetch_transactions(engine)
        print(f"Found {len(transactions)} transactions.")
        
    except Exception as e:
        print(f"Connection error: {e}")
        print("This is expected if no data has been loaded yet.")