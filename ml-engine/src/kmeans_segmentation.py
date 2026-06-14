"""
K-Means Clustering for Customer Segmentation
Advanced segmentation using RFM features
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


def prepare_features(rfm_df):
    """Prepare and scale features for clustering."""
    features = rfm_df[['recency', 'frequency', 'monetary']].copy()
    
    # Log transform to handle skewed distributions
    features['recency_log'] = np.log1p(features['recency'])
    features['frequency_log'] = np.log1p(features['frequency'])
    features['monetary_log'] = np.log1p(features['monetary'])
    
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features[['recency_log', 'frequency_log', 'monetary_log']])
    
    return scaled_features, scaler, features


def find_optimal_clusters(scaled_features, max_k=10):
    """Find optimal number of clusters using Elbow Method and Silhouette Score."""
    inertias = []
    silhouette_scores = []
    
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled_features)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(scaled_features, labels))
    
    # Find best k (highest silhouette score)
    best_k = silhouette_scores.index(max(silhouette_scores)) + 2
    
    return best_k, inertias, silhouette_scores


def perform_clustering(rfm_df, n_clusters=5):
    """Perform K-Means clustering and return labeled dataframe."""
    scaled_features, scaler, features = prepare_features(rfm_df)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm_df['cluster'] = kmeans.fit_predict(scaled_features)
    
    return rfm_df, kmeans, scaler


def label_clusters(rfm_df):
    """Assign meaningful labels to clusters based on their characteristics."""
    cluster_stats = rfm_df.groupby('cluster').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean'
    }).round(2)
    
    # Rank clusters
    r_score = pd.qcut(cluster_stats['recency'].rank(), 5, labels=['High', 'Medium-High', 'Medium', 'Medium-Low', 'Low'])
    f_score = pd.qcut(cluster_stats['frequency'].rank(), 5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
    m_score = pd.qcut(cluster_stats['monetary'].rank(), 5, labels=['Low', 'Medium-Low', 'Medium', 'Medium-High', 'High'])
    
    # Define segment mapping based on cluster characteristics
    def assign_segment(recency_rank, freq_rank):
        rec = str(recency_rank)
        freq = str(freq_rank)
        
        if rec in ['High', 'Medium-High'] and freq in ['High', 'Medium-High']:
            return 'Champions'
        elif rec in ['High', 'Medium-High'] and freq == 'Medium':
            return 'Loyal Customers'
        elif rec == 'Medium' and freq in ['High', 'Medium-High']:
            return 'Potential Loyalists'
        elif rec in ['Medium-Low', 'Low'] and freq in ['Medium-Low', 'Low']:
            return 'Lost Customers'
        elif rec in ['Medium-Low', 'Low']:
            return 'At Risk'
        else:
            return 'Needs Attention'
    
    mapping = {}
    for cluster_id in cluster_stats.index:
        mapping[cluster_id] = assign_segment(r_score[cluster_id], f_score[cluster_id])
    
    rfm_df['segment'] = rfm_df['cluster'].map(mapping)
    
    return rfm_df, cluster_stats


def generate_cluster_report(rfm_df):
    """Generate comprehensive cluster analysis report."""
    report = rfm_df.groupby('segment').agg(
        customer_count=('customer_id', 'count'),
        avg_recency=('recency', 'mean'),
        avg_frequency=('frequency', 'mean'),
        avg_monetary=('monetary', 'mean'),
        total_revenue=('monetary', 'sum')
    ).round(2)
    
    report['revenue_pct'] = (report['total_revenue'] / report['total_revenue'].sum() * 100).round(1)
    report['customer_pct'] = (report['customer_count'] / report['customer_count'].sum() * 100).round(1)
    
    return report


if __name__ == "__main__":
    # Generate sample data
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
    df['order_date'] = pd.to_datetime(df['order_date'])
    reference_date = datetime.now()
    
    # Calculate RFM
    rfm = df.groupby('customer_id').agg(
        recency=('order_date', lambda x: (reference_date - x.max()).days),
        frequency=('order_id', 'count'),
        monetary=('amount', 'sum')
    ).reset_index()
    
    print("=== Finding Optimal Clusters ===")
    scaled_features, _, _ = prepare_features(rfm)
    best_k, inertias, sil_scores = find_optimal_clusters(scaled_features)
    print(f"Optimal number of clusters: {best_k}")
    print(f"Silhouette scores: {[round(s, 3) for s in sil_scores]}")
    
    # Perform clustering
    rfm, kmeans_model, scaler = perform_clustering(rfm, n_clusters=best_k)
    
    # Label clusters
    rfm, cluster_stats = label_clusters(rfm)
    print("\n=== Cluster Statistics ===")
    print(cluster_stats)
    
    # Generate report
    report = generate_cluster_report(rfm)
    print("\n=== Final Segment Report ===")
    print(report)
    
    print(f"\nTotal Customers: {len(rfm)}")
    print(f"Number of Segments: {rfm['segment'].nunique()}")