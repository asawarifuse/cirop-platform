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

```bash
git clone https://github.com/asawarifuse/cirop-platform.git
cd cirop-platform
docker compose up -d
cd backend && npm install && npm run dev

📅 Build Log

Day 1 — Environment Setup ✅
Installed Docker Desktop with WSL 2 and Ubuntu
Verified Node.js v24.13.0, Python 3.14.2, Git 2.52.0

Day 2 — Project Foundation ✅
Created monorepo structure (frontend, backend, ml-engine, database, powerbi, docker, docs)
Initialized Git, pushed to GitHub
Added .gitignore, README with all rights reserved notice

Day 3 — Docker Compose Setup ✅
5 services: PostgreSQL App (5432), PostgreSQL Analytics (5433), Redis (6379), Redpanda (19092), MLflow (5000)
All containers health-checked and running

Day 4 — Database Schema Design ✅
App DB: users, refresh_tokens, scenario_presets
Analytics DB: Star schema — dim_customer, dim_product, dim_date, fact_transactions, fact_customer_snapshot
14 indexes, generated columns, foreign keys
Seeded dim_date with 2,557 rows (2020-2026)

Day 5 — Backend Initialization ✅
Node.js + Express server on port 3001
Prisma ORM v5 connected to PostgreSQL
Health check endpoint: GET /api/health

Day 6 — Authentication System ✅
JWT access tokens (15min) + refresh token rotation (7 days)
Bcrypt hashing (12 salt rounds), role-based access (Admin, Analyst, Executive)
Rate limiting on login, 4 endpoints tested

Day 7 — Customer Management API ✅
GET /customers — pagination, segment filter, search
GET /customers/:id — scorecard + predictions + recent orders
Protected by JWT middleware

Day 8 — Order Analytics API ✅
Revenue trends, product performance, purchase frequency, AOV by segment and channel

Day 9 — ML Engine & RFM Analysis ✅
Python virtual environment, pandas, numpy, scikit-learn
RFM module: 5-tier quintile scoring, 6 customer segments

Day 10 — K-Means Clustering & DB Connection ✅
Elbow + Silhouette for optimal clusters
PostgreSQL connection via SQLAlchemy

Day 11 — Seed Realistic Sample Data ✅
500 customers, 50 products, 5,000 transactions
Total revenue: $501,972.85

Day 12 — Customer Segmentation on Real Data ✅
498 customers → 5 segments
Champions: 93 (18.7% customers, 26.1% revenue)
Loyal: 80 | Potential Loyalists: 63 | At Risk: 63 | Lost: 199

Day 13 — CLV Prediction ✅
BG/NBD + Gamma-Gamma models
12-month CLV: Avg $589.81, Total $287,825.88
Top customer CLV: $2,081.73

👤 Author
Built solo over 75 days by @asawarifuse

Status: In Progress (Day 13/75)

📜 License
This project is not licensed for use, modification, or distribution. All rights reserved.