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
### Day 2 — Project Foundation ✅
### Day 3 — Docker Compose Setup ✅
### Day 4 — Database Schema Design ✅
### Day 5 — Backend Initialization ✅
### Day 6 — Authentication System ✅
### Day 7 — Customer Management API ✅
### Day 8 — Order Analytics API ✅
### Day 9 — ML Engine & RFM Analysis ✅
### Day 10 — K-Means Clustering & DB Connection ✅
### Day 11 — Seed Realistic Sample Data ✅
### Day 12 — Customer Segmentation on Real Data ✅
### Day 13 — CLV Prediction with BG/NBD & Gamma-Gamma ✅
### Day 14 — Churn Prediction ✅
### Day 15 — Revenue Forecasting with Prophet ✅
### Day 16 — Scenario Simulator ✅
### Day 17 — ML Predictions API (FastAPI) ✅
### Day 18 — Connect Backend to ML API ✅
### Day 19 — React Frontend Setup ✅
### Day 20 — Login Page & Auth Store ✅
### Day 21 — Dashboard Layout & KPI Cards ✅
### Day 22 — Customer List Page ✅
### Day 23 — Analytics Page with Charts ✅
### Day 24 — Predictions Page with Real ML Data ✅
### Day 25 — Scenarios Page ✅
### Day 26  — Backend Real Data Integration ✅

## 👤 Author
Built solo over 75 days by @asawarifuse

Status: In Progress (Day 16/75)

## 📜 License
This project is not licensed for use, modification, or distribution. All rights reserved.
