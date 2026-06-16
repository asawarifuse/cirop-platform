"""
Seed Data Generator for CIROP Analytics Database
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
from sqlalchemy import create_engine, text

np.random.seed(42)
random.seed(42)

DB_URL = "postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics"
engine = create_engine(DB_URL)

print("Clearing existing data...")
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE fact_transactions, dim_customer, dim_product CASCADE"))
    conn.commit()
print("  Tables cleared")

N_CUSTOMERS = 500
N_PRODUCTS = 50
N_TRANSACTIONS = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

first_names = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 'David', 'Elizabeth']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'London', 'Toronto', 'Sydney']
countries = ['USA', 'USA', 'USA', 'USA', 'UK', 'Canada', 'Australia']
channels = ['Organic', 'Paid_Search', 'Referral', 'Direct', 'Partner']

print("Generating customers...")
customers = []
for i in range(N_CUSTOMERS):
    country = random.choice(countries)
    signup = START_DATE + timedelta(days=random.randint(0, 600))
    customers.append({
        'customer_bk': str(uuid.uuid4()),
        'first_name': random.choice(first_names),
        'last_name': random.choice(last_names),
        'email': f'customer{i}@example.com',
        'city': random.choice(cities),
        'state': 'CA' if country == 'USA' else 'N/A',
        'country': country,
        'signup_date': signup.strftime('%Y-%m-%d'),
        'acquisition_channel': random.choice(channels),
        'current_segment': 'Unassigned',
    })

df_cust = pd.DataFrame(customers)
df_cust.to_sql('dim_customer', engine, if_exists='append', index=False)
print(f"  {len(df_cust)} customers created")

print("Generating products...")
product_list = [
    ('Wireless Headphones', 'Electronics', 'Audio', 149.99, 80.00),
    ('Bluetooth Speaker', 'Electronics', 'Audio', 79.99, 40.00),
    ('USB-C Hub', 'Electronics', 'Accessories', 49.99, 25.00),
    ('Laptop Stand', 'Electronics', 'Accessories', 39.99, 18.00),
    ('Wireless Mouse', 'Electronics', 'Peripherals', 29.99, 12.00),
    ('Mechanical Keyboard', 'Electronics', 'Peripherals', 89.99, 45.00),
    ('Running Shoes', 'Sports', 'Footwear', 129.99, 65.00),
    ('Yoga Mat', 'Sports', 'Equipment', 39.99, 15.00),
    ('Resistance Bands', 'Sports', 'Equipment', 24.99, 8.00),
    ('Water Bottle', 'Sports', 'Accessories', 19.99, 6.00),
    ('Coffee Maker', 'Home', 'Kitchen', 89.99, 40.00),
    ('Desk Lamp', 'Home', 'Office', 59.99, 25.00),
    ('Throw Pillow', 'Home', 'Decor', 29.99, 10.00),
    ('Wall Art', 'Home', 'Decor', 49.99, 20.00),
    ('Plant Pot', 'Home', 'Garden', 24.99, 8.00),
    ('Novel - Mystery', 'Books', 'Fiction', 14.99, 5.00),
    ('Cookbook', 'Books', 'Non-Fiction', 29.99, 12.00),
    ('Programming Guide', 'Books', 'Education', 49.99, 20.00),
    ('Notebook Set', 'Books', 'Stationery', 19.99, 7.00),
    ('Desk Organizer', 'Books', 'Stationery', 34.99, 14.00),
]

products = []
for i in range(N_PRODUCTS):
    if i < len(product_list):
        name, cat, subcat, price, cost = product_list[i]
    else:
        cat = random.choice(['Electronics', 'Sports', 'Home', 'Books'])
        name = f'Product {cat} {i+1}'
        subcat = f'Subcat {random.randint(1,5)}'
        price = round(random.uniform(9.99, 199.99), 2)
        cost = round(price * random.uniform(0.3, 0.6), 2)
    
    products.append({
        'product_bk': str(uuid.uuid4()),
        'name': name,
        'category': cat,
        'subcategory': subcat,
        'unit_price': price,
        'unit_cost': cost
    })

df_prod = pd.DataFrame(products)
df_prod.to_sql('dim_product', engine, if_exists='append', index=False)
print(f"  {len(df_prod)} products created")

print("Generating transactions...")
statuses = ['Completed', 'Completed', 'Completed', 'Returned', 'Cancelled']

transactions = []
for t in range(N_TRANSACTIONS):
    cust_idx = random.randint(0, N_CUSTOMERS - 1)
    prod_idx = random.randint(0, N_PRODUCTS - 1)
    
    cust_signup = datetime.strptime(customers[cust_idx]['signup_date'], '%Y-%m-%d')
    days_range = (END_DATE - cust_signup).days
    order_date = cust_signup + timedelta(days=random.randint(1, max(1, days_range)))
    
    prod = products[prod_idx]
    qty = random.choices([1, 1, 1, 2, 3], weights=[0.5, 0.3, 0.1, 0.07, 0.03])[0]
    
    transactions.append({
        'transaction_bk': str(uuid.uuid4()),
        'customer_sk': cust_idx + 1,
        'product_sk': prod_idx + 1,
        'order_date_sk': order_date.strftime('%Y-%m-%d'),
        'quantity': qty,
        'unit_price': prod['unit_price'],
        'discount_amount': round(random.uniform(0, 5), 2),
        'order_status': random.choice(statuses),
        'payment_method': random.choice(['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay'])
    })

df_txn = pd.DataFrame(transactions)
df_txn.to_sql('fact_transactions', engine, if_exists='append', index=False)
print(f"  {df_txn.shape[0]} transactions created")

print("\n=== Verification ===")
with engine.connect() as conn:
    cust_count = conn.execute(text("SELECT COUNT(*) FROM dim_customer")).scalar()
    prod_count = conn.execute(text("SELECT COUNT(*) FROM dim_product")).scalar()
    txn_count = conn.execute(text("SELECT COUNT(*) FROM fact_transactions")).scalar()
    rev = conn.execute(text("SELECT SUM(net_revenue) FROM fact_transactions")).scalar()
    
    print(f"Customers:    {cust_count}")
    print(f"Products:     {prod_count}")
    print(f"Transactions: {txn_count}")
    print(f"Total Revenue: ${rev:,.2f}")

print("\nDone! Database is ready for analytics.")