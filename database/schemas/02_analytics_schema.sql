-- ============================================
-- CIROP ANALYTICS DATABASE SCHEMA (Star Schema)
-- ============================================

-- DIMENSION: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_sk         SERIAL PRIMARY KEY,
    customer_bk         UUID UNIQUE NOT NULL,
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    email               VARCHAR(255),
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100),
    signup_date         DATE NOT NULL,
    acquisition_channel VARCHAR(50) CHECK (acquisition_channel IN 
                           ('Organic', 'Paid_Search', 'Referral', 'Direct', 'Partner')),
    current_segment     VARCHAR(30),
    is_active           BOOLEAN DEFAULT true,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- DIMENSION: Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_sk          SERIAL PRIMARY KEY,
    product_bk          UUID UNIQUE NOT NULL,
    name                VARCHAR(200) NOT NULL,
    category            VARCHAR(100) NOT NULL,
    subcategory         VARCHAR(100),
    unit_price          DECIMAL(10,2) NOT NULL,
    unit_cost           DECIMAL(10,2) NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- DIMENSION: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_pk             DATE PRIMARY KEY,
    year                INT NOT NULL,
    quarter             INT NOT NULL,
    month               INT NOT NULL,
    month_name          VARCHAR(20) NOT NULL,
    week_of_year        INT NOT NULL,
    day_of_week         VARCHAR(10) NOT NULL,
    is_weekend          BOOLEAN NOT NULL
);

-- FACT: Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_sk      SERIAL PRIMARY KEY,
    transaction_bk      UUID UNIQUE NOT NULL,
    customer_sk         INT REFERENCES dim_customer(customer_sk),
    product_sk          INT REFERENCES dim_product(product_sk),
    order_date_sk       DATE REFERENCES dim_date(date_pk),
    quantity            INT NOT NULL,
    unit_price          DECIMAL(10,2) NOT NULL,
    discount_amount     DECIMAL(10,2) DEFAULT 0,
    net_revenue         DECIMAL(12,2) GENERATED ALWAYS AS 
                           ((quantity * unit_price) - discount_amount) STORED,
    order_status        VARCHAR(20) DEFAULT 'Completed' CHECK (order_status IN 
                           ('Completed', 'Returned', 'Cancelled', 'Refunded')),
    payment_method      VARCHAR(30),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- FACT: Customer Monthly Snapshot (for ML features)
CREATE TABLE IF NOT EXISTS fact_customer_snapshot (
    snapshot_sk         SERIAL PRIMARY KEY,
    customer_sk         INT REFERENCES dim_customer(customer_sk),
    snapshot_month_sk   DATE REFERENCES dim_date(date_pk),
    recency_days        INT NOT NULL,
    frequency           INT NOT NULL,
    monetary_value      DECIMAL(12,2) NOT NULL,
    avg_order_value     DECIMAL(10,2),
    segment             VARCHAR(30),
    predicted_clv_12m   DECIMAL(10,2),
    churn_probability   FLOAT,
    predicted_next_purchase_days INT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_fact_txn_customer ON fact_transactions(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_txn_date ON fact_transactions(order_date_sk);
CREATE INDEX IF NOT EXISTS idx_fact_txn_product ON fact_transactions(product_sk);
CREATE INDEX IF NOT EXISTS idx_fact_snapshot_customer ON fact_customer_snapshot(customer_sk);
CREATE INDEX IF NOT EXISTS idx_fact_snapshot_month ON fact_customer_snapshot(snapshot_month_sk);
CREATE INDEX IF NOT EXISTS idx_dim_customer_segment ON dim_customer(current_segment);