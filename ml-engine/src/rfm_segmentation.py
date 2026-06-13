"""
RFM Segmentation Module
Recency, Frequency, Monetary analysis for customer segmentation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_rfm(df, reference_date=None):
    """
    Calculate RFM scores from transaction data.
    
    Parameters:
    df: DataFrame with columns - customer_id, order_date, amount
    reference_date: Date to calculate recency from (default: today)
    
    Returns:
    DataFrame with customer_id, recency, frequency, monetary, r_score, f_score, m_score, rfm_score
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Group by customer
    rfm = df.groupby('customer_id').agg({
        'order_date': lambda x: (reference_date - x.max()).days,  # Recency
        'order_id': 'count',                                       # Frequency
        'amount': 'sum'                                            # Monetary
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Score RFM (1=worst, 5=best)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    # Combined RFM score
    rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)
    
    return rfm


def segment_customers(rfm_df):
    """
    Segment customers based on RFM scores.
    
    Returns:
    DataFrame with segment labels
    """
    conditions = [
        (rfm_df['r_score'].astype(int) >= 4) & (rfm_df['f_score'].astype(int) >= 4) & (rfm_df['m_score'].astype(int) >= 4),
        (rfm_df['r_score'].astype(int) >= 4) & (rfm_df['f_score'].astype(int) >= 3),
        (rfm_df['r_score'].astype(int) >= 3) & (rfm_df['f_score'].astype(int) >= 4),
        (rfm_df['r_score'].astype(int) >= 3) & (rfm_df['f_score'].astype(int) <= 2),
        (rfm_df['r_score'].astype(int) <= 2) & (rfm_df['f_score'].astype(int) <= 2),
    ]
    
    choices = [
        'Champions',
        'Loyal Customers',
        'Potential Loyalists',
        'At Risk',
        'Lost Customers',
    ]
    
    rfm_df['segment'] = np.select(conditions, choices, default='Needs Attention')
    
    return rfm_df


def generate_segment_summary(rfm_df):
    """Generate summary statistics for each segment."""
    summary = rfm_df.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': ['mean', 'sum']
    }).round(2)
    
    summary.columns = ['customer_count', 'avg_recency_days', 'avg_frequency', 'avg_monetary', 'total_revenue']
    summary['revenue_pct'] = (summary['total_revenue'] / summary['total_revenue'].sum() * 100).round(1)
    
    return summary


if __name__ == "__main__":
    # Generate sample data for testing
    np.random.seed(42)
    n_customers = 1000
    n_transactions = 5000
    
    customer_ids = [f'CUST-{i:04d}' for i in range(n_customers)]
    
    data = []
    for _ in range(n_transactions):
        data.append({
            'order_id': f'ORD-{_:05d}',
            'customer_id': np.random.choice(customer_ids),
            'order_date': datetime.now() - timedelta(days=np.random.randint(1, 365)),
            'amount': np.random.uniform(10, 500)
        })
    
    df = pd.DataFrame(data)
    
    # Calculate RFM
    rfm = calculate_rfm(df)
    print("\n=== RFM Scores (First 10 customers) ===")
    print(rfm.head(10))
    
    # Segment customers
    rfm = segment_customers(rfm)
    print("\n=== Customer Segments ===")
    print(rfm['segment'].value_counts())
    
    # Summary
    summary = generate_segment_summary(rfm)
    print("\n=== Segment Summary ===")
    print(summary)