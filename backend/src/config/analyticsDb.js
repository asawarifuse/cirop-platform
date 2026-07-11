const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.ANALYTICS_URL || process.env.DATABASE_URL || 'postgresql://cirop_user:cirop_pass_2024@localhost:5433/cirop_analytics',
  ssl: { rejectUnauthorized: false },
});

module.exports = pool;