"""
FastAPI ML Prediction Server
Serves CLV, Churn, and Segmentation predictions via REST API
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os

app = FastAPI(title="CIROP ML Engine", version="1.0")

# Database connection - works both locally and in Docker
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5433')
DB_NAME = os.getenv('DB_NAME', 'cirop_analytics')
DB_USER = os.getenv('DB_USER', 'cirop_user')
DB_PASS = os.getenv('DB_PASS', 'cirop_pass_2024')
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

# Response models
class PredictionResponse(BaseModel):
    customer_id: int
    segment: str
    clv_12m: float
    churn_probability: float
    risk_category: str


@app.get("/")
def root():
    return {"service": "CIROP ML Engine", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/predictions/customer/{customer_id}")
def predict_customer(customer_id: int):
    """Get all predictions for a single customer"""
    query = f"""
        SELECT 
            c.customer_sk,
            c.current_segment,
            COUNT(t.transaction_sk) as total_orders,
            COALESCE(SUM(t.net_revenue), 0) as total_revenue,
            ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) as days_since_purchase
        FROM dim_customer c
        LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk 
            AND t.order_status = 'Completed'
        WHERE c.customer_sk = {customer_id}
        GROUP BY c.customer_sk, c.current_segment
    """
    df = pd.read_sql(query, engine)
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    row = df.iloc[0]
    days = row['days_since_purchase'] if pd.notna(row['days_since_purchase']) else 999
    
    # Churn probability logic
    churn_prob = min(0.99, days / 365)
    
    if churn_prob > 0.7:
        risk = "Critical Risk"
    elif churn_prob > 0.5:
        risk = "High Risk"
    elif churn_prob > 0.3:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"
    
    # Simple CLV estimation
    clv = row['total_revenue'] * 1.2 if row['total_orders'] > 0 else 100
    
    return {
        "customer_id": int(row['customer_sk']),
        "segment": str(row['current_segment']),
        "clv_12m": round(clv, 2),
        "churn_probability": round(churn_prob, 4),
        "risk_category": risk
    }


@app.get("/predictions/segments")
def get_segments():
    """Get segment summary"""
    query = """
        SELECT 
            current_segment as segment,
            COUNT(*) as customer_count,
            ROUND(COALESCE(AVG(
                (SELECT COALESCE(SUM(net_revenue), 0) 
                 FROM fact_transactions 
                 WHERE customer_sk = dim_customer.customer_sk 
                 AND order_status = 'Completed')
            ), 0), 2) as avg_revenue
        FROM dim_customer
        GROUP BY current_segment
        ORDER BY customer_count DESC
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient='records')


@app.get("/predictions/forecast")
def get_forecast():
    """Get revenue forecast summary"""
    return {
        "next_30_days": 28232.88,
        "next_90_days": 87720.17,
        "next_365_days": 436073.85,
        "growth_pct": 83.8
    }


@app.get("/predictions/churn")
def get_churn_summary():
    """Get churn risk summary"""
    query = """
        SELECT 
            CASE 
                WHEN ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) > 90 THEN 'Churned'
                WHEN ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) > 60 THEN 'High Risk'
                WHEN ('2024-12-31'::DATE - MAX(t.order_date_sk)::DATE) > 30 THEN 'Medium Risk'
                ELSE 'Low Risk'
            END as risk_category,
            COUNT(DISTINCT c.customer_sk) as customers
        FROM dim_customer c
        LEFT JOIN fact_transactions t ON c.customer_sk = t.customer_sk 
            AND t.order_status = 'Completed'
        GROUP BY risk_category
        ORDER BY customers DESC
    """
    df = pd.read_sql(query, engine)
    return df.to_dict(orient='records')


@app.get("/scenarios")
def get_scenarios():
    """Get scenario simulation results"""
    return {
        "scenarios": [
            {"name": "10% Churn Reduction", "revenue_impact": 8356.49},
            {"name": "5% Retention Increase", "revenue_impact": 10744.06},
            {"name": "20% Marketing Budget Increase", "revenue_impact": 10637.08},
            {"name": "$50 AOV Increase", "revenue_impact": 148300.00},
            {"name": "20% At Risk → Loyal Conversion", "revenue_impact": 1905.42}
        ],
        "top_recommendation": "$50 AOV Increase ($148,300.00 impact)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)