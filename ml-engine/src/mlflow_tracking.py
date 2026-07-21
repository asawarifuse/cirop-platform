"""
MLflow Experiment Tracking — Log models and metrics
"""

import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("cirop-churn-prediction")

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== MLflow Experiment Tracking ===\n")

# Fetch data
print("1. Fetching data...")
query = """
    SELECT 
        c.customer_sk, c.current_segment,
        COUNT(t.transaction_sk) as total_orders,
        COALESCE(SUM(t.net_revenue), 0) as total_revenue,
        ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) as days_since_purchase
    FROM dim_customer c
    LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk AND t.order_status = 'Completed'
    GROUP BY c.customer_sk, c.current_segment
"""
df = pd.read_sql(query, engine)
df['total_orders'] = df['total_orders'].fillna(0)
df['total_revenue'] = df['total_revenue'].fillna(0)
df['days_since_purchase'] = df['days_since_purchase'].fillna(999)
df['churned'] = (df['days_since_purchase'] > 90).astype(int)

X = df[['total_orders', 'total_revenue', 'days_since_purchase']].fillna(0)
y = df['churned']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"   Samples: {len(df)} | Features: {X.shape[1]}")

# Train with MLflow tracking
print("\n2. Training with MLflow tracking...")

with mlflow.start_run(run_name="random-forest-baseline"):
    # Log parameters
    params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
    mlflow.log_params(params)
    
    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Predict
    y_pred = model.predict(X_test)
    
    # Log metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
    }
    mlflow.log_metrics(metrics)
    
    # Log model
    mlflow.sklearn.log_model(model, "random-forest-model")
    
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   F1 Score:  {metrics['f1_score']:.4f}")

print(f"\n3. Experiment logged to MLflow!")
print(f"   View at: http://localhost:5000")