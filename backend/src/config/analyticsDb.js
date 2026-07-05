const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5433,
  database: 'cirop_analytics',
  user: 'cirop_user',
  password: 'cirop_pass_2024',
});

module.exports = pool;