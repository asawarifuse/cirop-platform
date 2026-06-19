# CIROP — Customer Intelligence & Revenue Optimization Platform

Enterprise analytics platform combining customer segmentation, CLV prediction, churn prediction, revenue forecasting, and executive decision support — built from scratch in 75 days.

---

## 🛠 Tech Stack

| Layer | Technology |
|:---|:---|
| Frontend | React, Redux Toolkit, Tailwind CSS |
| Backend | Node.js, Express, Prisma ORM |
| Database | PostgreSQL (OLTP + Analytics) |
| ML Engine | Python, scikit-learn, Lifetimes, XGBoost, Prophet |
| Streaming | Redpanda (Kafka-compatible) |
| MLOps | MLflow, Prefect, Evidently |
| BI | Power BI Desktop |
| Infrastructure | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## 📁 Folder Structure

cirop-platform/

├── frontend/ # React application

├── backend/ # Node.js + Express API
│ ├── src/controllers/
│ ├── src/middleware/
│ └── src/routes/

├── ml-engine/ # Python ML pipeline
│ └── src/

├── database/ # SQL schemas & seeds

├── powerbi/ # Power BI dashboards

├── docs/ # Documentation

├── docker-compose.yml

└── README.md

text

---

## 🚀 Quick Start

- git clone https://github.com/asawarifuse/cirop-platform.git
- cd cirop-platform
- docker compose up -d
- cd backend && npm install && npm run dev

## 📅 Build Log

### Day 1 — Environment Setup ✅
- Installed Docker Desktop with WSL 2 and Ubuntu
- Verified Node.js v24.13.0, Python 3.14.2, Git 2.52.0
- Docker Engine running successfully

### Day 2 — Project Foundation ✅
- Created monorepo structure (frontend, backend, ml-engine, database, powerbi, docker, docs, .github/workflows)
- Initialized Git, pushed to GitHub as public repo
- Added .gitignore (node_modules, venv, .env, __pycache__, mlruns, *.pkl, dist, logs)
- README with all rights reserved notice

### Day 3 — Docker Compose Setup ✅
- Created docker-compose.yml with 5 services
- PostgreSQL App (port 5432), PostgreSQL Analytics (port 5433)
- Redis Cache (port 6379) with healthcheck
- Redpanda Streaming (port 19092) — Kafka-compatible, single binary
- MLflow Tracking Server (port 5000) with PostgreSQL backend
- All 5 containers health-checked and running

### Day 4 — Database Schema Design ✅
- App DB (cirop_app): users, refresh_tokens, scenario_presets tables with UUID primary keys
- Analytics DB (cirop_analytics): Star schema — dim_customer, dim_product, dim_date, fact_transactions, fact_customer_snapshot
- Generated column: net_revenue = (quantity × unit_price) − discount_amount
- 14 indexes across all tables for query performance
- Seeded dim_date with 2,557 rows covering 2020-01-01 to 2026-12-31
- Schema applied to both databases via Docker exec

### Day 5 — Backend Initialization ✅
- Node.js project initialized with Express on port 3001
- Installed: express, cors, helmet, express-rate-limit, jsonwebtoken, bcryptjs, dotenv, winston
- Prisma ORM v5 installed and connected to PostgreSQL
- Defined models: User, RefreshToken, ScenarioPreset
- Generated Prisma client, pushed schema to database
- Health check endpoint: GET /api/health → { status, service, timestamp }
- Dev script with nodemon for auto-restart on file changes

### Day 6 — Authentication System ✅
- JWT access tokens with 15-minute expiry
- Refresh token rotation stored hashed in database (7-day expiry)
- Bcrypt password hashing with 12 salt rounds
- Role-based access control: Admin, Analyst, Executive
- Rate limiting on login: 10 attempts per 15 minutes per IP
- Auth middleware: authenticate() for JWT verification, authorize() for role check
- 4 endpoints: POST /api/v1/auth/register, login, refresh, logout
- Refresh tokens revoked on logout and on rotation
- Tested successfully with admin@cirop.com / Admin@123

### Day 7 — Customer Management API ✅
- GET /api/v1/customers — list with pagination (page, limit), segment filter, text search
- GET /api/v1/customers/:id — detailed profile with scorecard, ML predictions, recent orders
- Scorecard: total_orders, total_revenue, avg_order_value, purchase_frequency, days_since_last_purchase, lifetime_days
- Predictions: clv_12_months, churn_probability, predicted_next_purchase_days
- Both endpoints protected by JWT authentication middleware
- LinkedIn post published — Week 1 build story

### Day 8 — Order Analytics API ✅
- GET /orders/analytics/revenue — total_revenue, revenue_growth_pct, monthly trend, category breakdown
- GET /orders/analytics/products — top 5 products (revenue, units, rating), bottom 2 products
- GET /orders/analytics/frequency — avg_purchase_interval, frequency distribution (Weekly to Yearly), AOV trend
- GET /orders/analytics/aov — overall AOV, by segment (5 segments), by channel (5 channels)
- All endpoints JWT protected, structured mock data returned

### Day 9 — ML Engine & RFM Analysis ✅
- Created Python virtual environment in ml-engine/
- Installed: pandas, numpy, scikit-learn, matplotlib, seaborn, jupyter
- Built RFM segmentation module: calculate_rfm(), segment_customers(), generate_segment_summary()
- 5-tier quintile scoring (R, F, M scores 1-5 each), combined RFM score range 3-15
- 6 segments: Champions, Loyal Customers, Potential Loyalists, At Risk, Lost Customers, Needs Attention
- Segment summary with customer count, avg recency/frequency/monetary, revenue share
- Tested on 1,000 synthetic customers with 5,000 transactions

### Day 10 — K-Means Clustering & DB Connection ✅
- Feature preparation: log transform + StandardScaler for recency, frequency, monetary
- find_optimal_clusters(): Elbow method + Silhouette score for k=2 to 10
- perform_clustering(): K-Means with n_init=10, random_state=42
- label_clusters(): automatic segment naming based on cluster recency/frequency ranks
- PostgreSQL connection via SQLAlchemy + psycopg2-binary
- Read functions: fetch_customers(), fetch_transactions(), fetch_customer_snapshots()
- Write functions: write_segments(), write_predictions() with parameterized queries
- Virtual environment rebuilt from scratch due to corrupted packages

### Day 11 — Seed Realistic Sample Data ✅
- 500 customers: UUID business keys, 20 real first names, 20 real last names, 8 cities, 7 countries (USA/UK/Canada/Australia), 5 acquisition channels (Organic 35%, Paid Search 25%, Referral 20%, Direct 15%, Partner 5%)
- 50 products: 20 named (Wireless Headphones, Running Shoes, Coffee Maker, etc.) + 30 auto-generated, 4 categories (Electronics, Sports, Home, Books), unit_price and unit_cost for gross profit
- 5,000 transactions: UUID business keys, weighted quantities (50% qty=1), realistic dates within customer signup range, 5 statuses (Completed 75%, Returned 10%, Cancelled 5%), 4 payment methods
- Total revenue: $501,972.85 across 2,966 completed orders
- Data verified via PostgreSQL queries

### Day 12 — Customer Segmentation on Real Data ✅
- Fetched 2,938 completed order records from fact_transactions
- Calculated RFM scores for 498 customers (2 had zero completed orders)
- Applied rule-based segmentation logic
- Champions: 93 customers (18.7%) → $77,931.93 revenue (26.1%), avg recency 11.4 days
- Loyal Customers: 80 customers (16.1%) → $42,174.20 revenue (14.1%), avg recency 12.6 days
- Potential Loyalists: 63 customers (12.7%) → $46,346.68 revenue (15.5%)
- At Risk: 63 customers (12.7%) → $23,208.74 revenue (7.8%)
- Lost Customers: 199 customers (40.0%) → $108,784.55 revenue (36.5%), avg recency 137.9 days
- Segments written to dim_customer.current_segment column

### Day 13 — CLV Prediction with BG/NBD & Gamma-Gamma ✅
- Fetched 2,966 completed transactions from 498 customers
- Trained Beta-Geometric/NBD model for purchase frequency prediction
- Trained Gamma-Gamma model for monetary value prediction
- 12-month CLV: Average $589.81, Median $540.48, Maximum $2,081.73
- Total predicted 12-month revenue: $287,825.88
- CLV distribution: Very Low 0.8%, Low 43.0%, Medium 45.0%, High 9.2%
- Top customer (ID 372): Predicted CLV $2,081.73, 13.4 purchases, AOV $155.77
- Predictions stored in database

## 👤 Author
Built solo over 75 days by @asawarifuse

Status: In Progress (Day 13/75)

## 📜 License
This project is not licensed for use, modification, or distribution. All rights reserved.