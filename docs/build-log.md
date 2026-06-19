======================================================
CIROP BUILD LOG — Days 1 to 13
======================================================

Day 1 — Environment Setup ✅
- Installed Docker Desktop with WSL 2 and Ubuntu
- Verified Node.js v24.13.0, Python 3.14.2, Git 2.52.0
- Docker Engine running successfully

Day 2 — Project Foundation ✅
- Created monorepo: frontend, backend, ml-engine, database, powerbi, docker, docs, .github
- Initialized Git, pushed to GitHub
- Added .gitignore (node_modules, venv, .env, pycache, mlruns, pkl, dist, logs)
- README with project description, tech stack, all rights reserved notice

Day 3 — Docker Compose Setup ✅
- Created docker-compose.yml with 5 services
- PostgreSQL App (5432), PostgreSQL Analytics (5433)
- Redis Cache (6379), Redpanda Streaming (19092)
- MLflow Tracking Server (5000)
- All containers health-checked and running

Day 4 — Database Schema Design ✅
- App DB: users, refresh_tokens, scenario_presets tables
- Analytics DB: dim_customer, dim_product, dim_date, fact_transactions, fact_customer_snapshot
- 14 indexes, generated columns (net_revenue), foreign keys
- Seeded dim_date with 2,557 rows (2020-2026)
- Schema applied to both databases via Docker exec

Day 5 — Backend Initialization ✅
- Node.js + Express server on port 3001
- Prisma ORM v5 connected to PostgreSQL
- Models: User, RefreshToken, ScenarioPreset
- Prisma client generated, schema synced
- Health check: GET /api/health

Day 6 — Authentication System ✅
- JWT access tokens (15min) + refresh token rotation (7 days)
- Bcrypt password hashing (12 salt rounds)
- Role-based access: Admin, Analyst, Executive
- Rate limiting: 10 login attempts per 15 minutes
- Endpoints: Register, Login, Refresh, Logout
- Tested with admin@cirop.com

Day 7 — Customer Management API ✅
- GET /customers — list with pagination, segment filter, search
- GET /customers/:id — profile + scorecard + predictions + orders
- Protected by JWT authentication middleware
- Scorecard: orders, revenue, AOV, frequency, recency, lifetime
- Predictions: CLV, churn probability, next purchase

Day 8 — Order Analytics API ✅
- GET /orders/analytics/revenue — total, growth %, monthly trend, category breakdown
- GET /orders/analytics/products — top 5/bottom 2 with ratings
- GET /orders/analytics/frequency — intervals, distribution, AOV trend
- GET /orders/analytics/aov — by segment, by channel, overall
- All endpoints JWT protected

Day 9 — ML Engine & RFM Analysis ✅
- Python virtual environment created in ml-engine
- Installed: pandas, numpy, scikit-learn, matplotlib, seaborn
- RFM module: calculate_rfm(), segment_customers(), generate_segment_summary()
- 5-tier quintile scoring (R, F, M scores 1-5 each)
- 6 segments: Champions, Loyal, Potential Loyalists, At Risk, Lost, Needs Attention
- Tested on 1,000 synthetic customers

Day 10 — K-Means Clustering & DB Connection ✅
- K-Means with log transform + StandardScaler feature prep
- Elbow method + Silhouette score for optimal k
- Automatic cluster labeling based on recency/frequency ranks
- PostgreSQL connection via SQLAlchemy + psycopg2
- Read/write functions for dim_customer, fact_transactions, fact_customer_snapshot
- Virtual environment rebuilt from scratch

Day 11 — Seed Realistic Sample Data ✅
- 500 customers: UUID keys, real names, 8 cities, 7 countries, 5 channels
- 50 products: 20 named + 30 auto, 4 categories, unit_price + unit_cost
- 5,000 transactions: UUID keys, weighted quantities, 5 statuses, 4 payment methods
- Total revenue: $501,972.85 across 2,966 completed orders
- Data verified in PostgreSQL

Day 12 — Customer Segmentation Pipeline on Real Data ✅
- Fetched 2,938 completed orders from PostgreSQL
- RFM scores calculated for 498 customers
- Champions: 93 (18.7% customers, 26.1% revenue, avg recency 11.4 days)
- Loyal: 80 (16.1% customers, 14.1% revenue, avg recency 12.6 days)
- Potential Loyalists: 63 (12.7% customers, 15.5% revenue)
- At Risk: 63 (12.7% customers, 7.8% revenue)
- Lost: 199 (40.0% customers, 36.5% revenue, avg recency 137.9 days)
- Segments written to dim_customer table

Day 13 — CLV Prediction with BG/NBD & Gamma-Gamma ✅
- Fetched 2,966 transactions from 498 customers
- BG/NBD model trained for purchase frequency prediction
- Gamma-Gamma model trained for monetary value prediction
- 12-month CLV: Avg $589.81, Median $540.48, Max $2,081.73
- Total predicted 12-month revenue: $287,825.88
- CLV distribution: 45% Medium ($500-1K), 43% Low ($100-500), 9% High ($1K-5K)
- Top customer CLV: $2,081.73 (Customer 372, 13.4 predicted purchases)
- Predictions written to database