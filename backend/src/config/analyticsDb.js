const { Pool } = require('pg');

const connectionString = process.env.ANALYTICS_URL || process.env.DATABASE_URL;

const pool = new Pool({
  connectionString: connectionString,
  ssl: { rejectUnauthorized: false },
});

module.exports = pool;