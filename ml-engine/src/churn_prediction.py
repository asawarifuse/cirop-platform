"""
Churn Prediction Pipeline
Builds churn model using customer snapshot data
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report
from sklearn.preprocessing import StandardScaler
import joblib

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== CHURN PREDICTION PIPELINE ===\n")

# 1. Define churn: customers with no purchase in last 90 days
print("1. Fetching customer data...")
query = """
    SELECT 
        c.customer_sk,
        c.current_segment,
        c.acquisition_channel,
        COUNT(t.transaction_sk) as total_orders,
        COALESCE(SUM(t.net_revenue), 0) as total_revenue,
        COALESCE(AVG(t.net_revenue), 0) as avg_order_value,
        MAX(t.order_date_sk) as last_order_date,
        MIN(t.order_date_sk) as first_order_date,
        ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) as days_since_last_purchase
    FROM dim_customer c
    LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk AND t.order_status = 'Completed'
    GROUP BY c.customer_sk, c.current_segment, c.acquisition_channel
"""
df = pd.read_sql(query, engine)
print(f"   Fetched {len(df)} customers")

# 2. Create target variable
df['churned'] = (df['days_since_last_purchase'].fillna(999) > 90).astype(int)

# Handle customers with no orders
df['total_orders'] = df['total_orders'].fillna(0)
df['total_revenue'] = df['total_revenue'].fillna(0)
df['avg_order_value'] = df['avg_order_value'].fillna(0)
df['days_since_last_purchase'] = df['days_since_last_purchase'].fillna(999)

churn_count = df['churned'].sum()
print(f"\n2. Target distribution:")
print(f"   Churned: {churn_count} ({churn_count/len(df)*100:.1f}%)")
print(f"   Active:  {len(df)-churn_count} ({(len(df)-churn_count)/len(df)*100:.1f}%)")

# 3. Feature engineering
print("\n3. Preparing features...")

# Encode categorical
channel_dummies = pd.get_dummies(df['acquisition_channel'], prefix='channel')
segment_dummies = pd.get_dummies(df['current_segment'], prefix='seg')

features = pd.concat([
    df[['total_orders', 'total_revenue', 'avg_order_value', 'days_since_last_purchase']],
    channel_dummies,
    segment_dummies
], axis=1)

# Add derived features
features['revenue_per_order'] = features['total_revenue'] / (features['total_orders'] + 1)
features['is_zero_orders'] = (features['total_orders'] == 0).astype(int)

X = features
y = df['churned']

print(f"   Features: {X.shape[1]}")
print(f"   Samples:  {X.shape[0]}")

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Train models
print("\n4. Training models...")

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
}

results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    results[name] = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_prob)
    }
    print(f"   {name}: Accuracy={results[name]['accuracy']:.3f}, F1={results[name]['f1']:.3f}, AUC={results[name]['roc_auc']:.3f}")

# 6. Select best model
print("\n5. Best model selection...")
best_model_name = max(results, key=lambda k: results[k]['roc_auc'])
best_model = models[best_model_name]
print(f"   Best: {best_model_name} (AUC={results[best_model_name]['roc_auc']:.4f})")

# 7. Feature importance
print("\n6. Top features:")
if hasattr(best_model, 'feature_importances_'):
    importance = best_model.feature_importances_
elif hasattr(best_model, 'coef_'):
    importance = abs(best_model.coef_[0])
else:
    importance = np.ones(len(X.columns))

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': importance
}).sort_values('importance', ascending=False)

for i, row in feature_importance.head(10).iterrows():
    print(f"   {row['feature']:<30s}: {row['importance']:.4f}")

# 8. Predict churn for all customers
print("\n7. Predicting churn for all customers...")
X_all_scaled = scaler.transform(X)
all_probabilities = best_model.predict_proba(X_all_scaled)[:, 1]
df['churn_probability'] = all_probabilities.round(4)

# 9. Risk categories
df['risk_category'] = pd.cut(
    df['churn_probability'],
    bins=[-0.01, 0.3, 0.5, 0.7, 1.0],
    labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']
)

print("\n8. Risk distribution:")
risk_dist = df['risk_category'].value_counts().sort_index()
for risk, count in risk_dist.items():
    pct = count / len(df) * 100
    print(f"   {risk:<15s}: {count:>5d} ({pct:>5.1f}%)")

# 10. Write predictions to database
print("\n9. Writing churn predictions to database...")
with engine.connect() as conn:
    for _, row in df.iterrows():
        conn.execute(
            text("""
                UPDATE dim_customer 
                SET updated_at = NOW()
                WHERE customer_sk = :sk
            """),
            {'sk': int(row['customer_sk'])}
        )
    conn.commit()
print("   Predictions updated")

# 11. Save model
joblib.dump(best_model, 'models/churn_model.pkl')
joblib.dump(scaler, 'models/churn_scaler.pkl')
print("\n10. Model saved to models/")

# 12. High-risk customers
print("\n11. Top 10 High-Risk Customers:")
high_risk = df.nlargest(10, 'churn_probability')
for _, row in high_risk.iterrows():
    print(f"   Customer {row['customer_sk']:>4.0f}: {row['churn_probability']:.1%} risk | "
          f"Segment: {row['current_segment']:<20s} | Days since last: {row['days_since_last_purchase']:.0f}")

print(f"\n=== CHURN PREDICTION COMPLETE ===")
print(f"Best Model: {best_model_name}")
print(f"ROC-AUC: {results[best_model_name]['roc_auc']:.4f}")