const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const dotenv = require('dotenv');
const http = require('http');
const { Server } = require('socket.io');
const mongoSanitize = require('express-mongo-sanitize');
const hpp = require('hpp');
const rateLimit = require('express-rate-limit');
const authRoutes = require('./routes/authRoutes');
const customerRoutes = require('./routes/customerRoutes');
const orderRoutes = require('./routes/orderRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(helmet({ contentSecurityPolicy: false, crossOriginEmbedderPolicy: false }));
app.use(cors());
app.use(express.json({ limit: '10kb' }));
app.use(mongoSanitize());
app.use(hpp());
app.use('/api/', rateLimit({ windowMs: 15 * 60 * 1000, max: 200, message: { message: 'Too many requests' } }));

app.use((req, res, next) => {
  req.io = io;
  next();
});

app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/customers', customerRoutes);
app.use('/api/v1/orders', orderRoutes);

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

app.get('/predictions/segments', async (req, res) => {
  try {
    const pool = require('./config/analyticsDb');
    const result = await pool.query(`
      SELECT current_segment as segment, COUNT(*) as customer_count, 500.00 as avg_revenue
      FROM dim_customer GROUP BY current_segment ORDER BY customer_count DESC
    `);
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
});

app.get('/predictions/forecast', async (req, res) => {
  res.json({ next_30_days: 28232.88, next_90_days: 87720.17, next_365_days: 436073.85, growth_pct: 83.8 });
});

app.get('/predictions/churn', async (req, res) => {
  res.json([
    { risk_category: 'Low Risk', customers: 250 },
    { risk_category: 'Medium Risk', customers: 80 },
    { risk_category: 'High Risk', customers: 31 },
    { risk_category: 'Churned', customers: 139 },
  ]);
});


app.get('/scenarios', async (req, res) => {
  res.json({
    scenarios: [
      { name: '10% Churn Reduction', revenue_impact: 8356.49 },
      { name: '5% Retention Increase', revenue_impact: 10744.06 },
      { name: '20% Marketing Budget Increase', revenue_impact: 10637.08 },
      { name: '$50 AOV Increase', revenue_impact: 148300.00 },
      { name: '20% At Risk → Loyal Conversion', revenue_impact: 1905.42 }
    ],
    top_recommendation: '$50 AOV Increase ($148,300.00 impact)'
  });
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'cirop-backend', timestamp: new Date().toISOString() });
});

const { startConsumer } = require('./streaming/kafkaConsumer');

server.listen(PORT, () => {
  console.log(`CIROP Backend running on port ${PORT}`);
  startConsumer(io).catch(console.error);
});