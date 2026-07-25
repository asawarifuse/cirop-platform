import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

mlflow.set_tracking_uri("http://localhost:5000")
DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== MLflow Model Registry ===\n")

# 1. Fetch data
print("1. Loading training data...")
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
df = pd.read_sql(query, engine).fillna(0)
df['churned'] = (df['days_since_purchase'] > 90).astype(int)

X = df[['total_orders', 'total_revenue', 'days_since_purchase']]
y = df['churned']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"   {len(df)} samples | {len(X_train)} train | {len(X_test)} test")

# 2. Train multiple models and register the best
models = {
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    
}

best_model = None
best_score = 0
best_name = ""

for name, model in models.items():
    print(f"\n2. Training {name}...")
    
    with mlflow.start_run(run_name=f"{name}-v1"):
        mlflow.log_params({"model_type": name})
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
        }
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name)
        
        print(f"   Accuracy: {metrics['accuracy']:.4f} | F1: {metrics['f1_score']:.4f}")
        
        if metrics['f1_score'] > best_score:
            best_score = metrics['f1_score']
            best_model = model
            best_name = name

# 3. Register best model
print(f"\n3. Registering best model: {best_name} (F1: {best_score:.4f})")

with mlflow.start_run(run_name=f"{best_name}-production"):
    mlflow.log_params({"model_type": best_name, "stage": "production"})
    mlflow.log_metric("f1_score", best_score)
    mlflow.sklearn.log_model(best_model, "churn-predictor")

print(f"\n Model Registry: http://localhost:5000")
print(f" Best Model: {best_name}")
print(f" F1 Score: {best_score:.4f}")
print("\n=== Registry Complete ===")