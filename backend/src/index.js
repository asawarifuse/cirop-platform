const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const dotenv = require('dotenv');
const authRoutes = require('./routes/authRoutes');
const customerRoutes = require('./routes/customerRoutes');
const orderRoutes = require('./routes/orderRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(helmet());
app.use(cors({
  origin: ['http://localhost:3000', 'https://your-app.vercel.app'],
  credentials: true,
}));
app.use(express.json());

// Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/customers', customerRoutes);
app.use('/api/v1/orders', orderRoutes);

// Dashboard summary
app.get('/api/v1/dashboard/summary', async (req, res) => {
  try {
    const pool = require('./config/analyticsDb');
    const result = await pool.query(`
      SELECT 
        (SELECT COALESCE(SUM(net_revenue), 0) FROM fact_transactions WHERE order_status = 'Completed') as total_revenue,
        (SELECT COUNT(*) FROM dim_customer) as total_customers,
        (SELECT COUNT(*) FROM fact_transactions WHERE order_status = 'Completed') as total_orders,
        (SELECT ROUND(AVG(net_revenue), 2) FROM fact_transactions WHERE order_status = 'Completed') as avg_order_value
    `);
    res.json({ status: 'success', data: result.rows[0] });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'cirop-backend', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`CIROP Backend running on port ${PORT}`);
});
