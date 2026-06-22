"""
Revenue Forecasting Pipeline
Uses Prophet to predict future revenue from transaction data
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from prophet import Prophet
import matplotlib.pyplot as plt
from datetime import datetime

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("=== REVENUE FORECASTING PIPELINE ===\n")

# 1. Fetch daily revenue
print("1. Fetching daily revenue...")
query = """
    SELECT 
        order_date_sk as ds,
        SUM(net_revenue) as y
    FROM fact_transactions
    WHERE order_status = 'Completed'
    GROUP BY order_date_sk
    ORDER BY order_date_sk
"""
df = pd.read_sql(query, engine)
df['ds'] = pd.to_datetime(df['ds'])
print(f"   Fetched {len(df)} days of revenue data")
print(f"   Date range: {df['ds'].min().date()} to {df['ds'].max().date()}")
print(f"   Total revenue: ${df['y'].sum():,.2f}")
print(f"   Avg daily revenue: ${df['y'].mean():,.2f}")

# 2. Train Prophet model
print("\n2. Training Prophet model...")
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05
)
model.fit(df)
print("   Model trained")

# 3. Create future dataframe (next 12 months)
print("\n3. Creating future dataframe...")
future = model.make_future_dataframe(periods=365)
print(f"   Forecasting from {future['ds'].min().date()} to {future['ds'].max().date()}")

# 4. Predict
print("\n4. Generating forecast...")
forecast = model.predict(future)
print("   Forecast generated")

# 5. Extract results
print("\n5. Forecast Summary:")

# Next 30 days
next_30 = forecast[forecast['ds'] > df['ds'].max()].head(30)
revenue_30d = next_30['yhat'].sum()
print(f"   Next 30 days:     ${revenue_30d:>12,.2f}")

# Next 90 days
next_90 = forecast[forecast['ds'] > df['ds'].max()].head(90)
revenue_90d = next_90['yhat'].sum()
print(f"   Next 90 days:     ${revenue_90d:>12,.2f}")

# Next 180 days
next_180 = forecast[forecast['ds'] > df['ds'].max()].head(180)
revenue_180d = next_180['yhat'].sum()
print(f"   Next 180 days:    ${revenue_180d:>12,.2f}")

# Next 365 days
next_365 = forecast[forecast['ds'] > df['ds'].max()]
revenue_365d = next_365['yhat'].sum()
print(f"   Next 365 days:    ${revenue_365d:>12,.2f}")

# Monthly breakdown
forecast['month'] = forecast['ds'].dt.to_period('M')
future_only = forecast[forecast['ds'] > df['ds'].max()]
monthly = future_only.groupby('month').agg(
    forecasted_revenue=('yhat', 'sum'),
    lower_bound=('yhat_lower', 'sum'),
    upper_bound=('yhat_upper', 'sum')
).round(2)

print("\n6. Monthly Forecast (Next 12 Months):")
print("-" * 60)
for month, row in monthly.head(12).iterrows():
    print(f"   {month}: ${row['forecasted_revenue']:>10,.2f}  (${row['lower_bound']:>10,.2f} - ${row['upper_bound']:>10,.2f})")

# 6. Yearly comparison
print("\n7. Yearly Comparison:")
actual_2023 = df[df['ds'].dt.year == 2023]['y'].sum()
actual_2024 = df[df['ds'].dt.year == 2024]['y'].sum()
predicted_2025 = future_only[future_only['ds'].dt.year == 2025]['yhat'].sum()

print(f"   2023 Actual:    ${actual_2023:>12,.2f}")
print(f"   2024 Actual:    ${actual_2024:>12,.2f}")
print(f"   2025 Forecast:  ${predicted_2025:>12,.2f}")

if actual_2024 > 0:
    growth = ((predicted_2025 - actual_2024) / actual_2024) * 100
    print(f"   YoY Growth:     {growth:>11.1f}%")

# 7. Save forecast data
print("\n8. Saving forecast...")
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv('data/revenue_forecast.csv', index=False)
print("   Saved to data/revenue_forecast.csv")

# 8. Key insights
print("\n9. Key Insights:")
best_month = monthly.nlargest(1, 'forecasted_revenue')
worst_month = monthly.nsmallest(1, 'forecasted_revenue')
print(f"   Best month:  {best_month.index[0]} (${best_month['forecasted_revenue'].values[0]:,.2f})")
print(f"   Worst month: {worst_month.index[0]} (${worst_month['forecasted_revenue'].values[0]:,.2f})")

avg_monthly = monthly['forecasted_revenue'].mean()
print(f"   Avg monthly forecast: ${avg_monthly:,.2f}")

print(f"\n=== FORECAST COMPLETE ===")