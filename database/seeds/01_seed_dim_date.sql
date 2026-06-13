-- ============================================
-- SEED: Populate Date Dimension (2020-2026)
-- ============================================

INSERT INTO dim_date (date_pk, year, quarter, month, month_name, week_of_year, day_of_week, is_weekend)
SELECT 
    d::DATE,
    EXTRACT(YEAR FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(MONTH FROM d)::INT,
    TRIM(TO_CHAR(d, 'Month')),
    EXTRACT(WEEK FROM d)::INT,
    TRIM(TO_CHAR(d, 'Day')),
    CASE WHEN EXTRACT(DOW FROM d) IN (0, 6) THEN true ELSE false END
FROM generate_series('2020-01-01'::DATE, '2026-12-31'::DATE, '1 day'::INTERVAL) d
ON CONFLICT (date_pk) DO NOTHING;