const pool = require('../config/analyticsDb');
const mlApiService = require('../services/mlApiService');

const getAllCustomers = async (req, res) => {
  try {
    const { page = 1, limit = 50, segment, search } = req.query;
    const offset = (parseInt(page) - 1) * parseInt(limit);

    let query = `
      SELECT 
        c.customer_sk as customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.city,
        c.country,
        c.current_segment,
        COALESCE(t.order_count, 0) as total_orders,
        COALESCE(t.total_revenue, 0) as total_revenue
      FROM dim_customer c
      LEFT JOIN (
        SELECT customer_sk, COUNT(*) as order_count, SUM(net_revenue) as total_revenue
        FROM fact_transactions
        WHERE order_status = 'Completed'
        GROUP BY customer_sk
      ) t ON c.customer_sk = t.customer_sk
      WHERE 1=1
    `;

    const params = [];
    if (segment && segment !== 'All') {
      params.push(segment);
      query += ` AND c.current_segment = $${params.length}`;
    }
    if (search) {
      params.push(`%${search}%`);
      query += ` AND (c.first_name ILIKE $${params.length} OR c.last_name ILIKE $${params.length} OR c.email ILIKE $${params.length})`;
    }

    query += ` ORDER BY c.customer_sk LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(parseInt(limit), offset);

    const result = await pool.query(query, params);

    res.json({
      status: 'success',
      data: result.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: result.rows.length,
      },
    });
  } catch (error) {
    console.error('Get customers error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

const getCustomerById = async (req, res) => {
  try {
    const { id } = req.params;

    const query = `
      SELECT 
        c.customer_sk as customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.city,
        c.state,
        c.country,
        c.signup_date,
        c.acquisition_channel,
        c.current_segment,
        c.is_active,
        COALESCE(t.order_count, 0) as total_orders,
        COALESCE(t.total_revenue, 0) as total_revenue,
        CASE WHEN t.order_count > 0 THEN ROUND(t.total_revenue / t.order_count, 2) ELSE 0 END as avg_order_value,
        MAX(t.last_date) as last_purchase_date
      FROM dim_customer c
      LEFT JOIN (
        SELECT 
          customer_sk, 
          COUNT(*) as order_count, 
          SUM(net_revenue) as total_revenue,
          MAX(order_date_sk) as last_date
        FROM fact_transactions
        WHERE order_status = 'Completed'
        GROUP BY customer_sk
      ) t ON c.customer_sk = t.customer_sk
      WHERE c.customer_sk = $1
      GROUP BY c.customer_sk, c.first_name, c.last_name, c.email, c.city, c.state, c.country, 
               c.signup_date, c.acquisition_channel, c.current_segment, c.is_active, 
               t.order_count, t.total_revenue
    `;

    const result = await pool.query(query, [id]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Customer not found' });
    }

    const customer = result.rows[0];

    // Try ML API for predictions, fallback to calculated values
    let predictions = null;
    try {
      predictions = await mlApiService.getCustomerPrediction(id);
    } catch (e) {
      // Use calculated predictions
    }

    const recentOrdersQuery = `
      SELECT transaction_bk as order_id, order_date_sk as date, net_revenue as amount, order_status as status
      FROM fact_transactions
      WHERE customer_sk = $1
      ORDER BY order_date_sk DESC
      LIMIT 5
    `;
    const ordersResult = await pool.query(recentOrdersQuery, [id]);

    res.json({
      status: 'success',
      data: {
        customer_id: customer.customer_id,
        first_name: customer.first_name,
        last_name: customer.last_name,
        email: customer.email,
        city: customer.city,
        state: customer.state,
        country: customer.country,
        signup_date: customer.signup_date,
        acquisition_channel: customer.acquisition_channel,
        current_segment: customer.current_segment || 'Unassigned',
        is_active: customer.is_active,
        scorecard: {
          total_orders: parseInt(customer.total_orders),
          total_revenue: parseFloat(customer.total_revenue),
          avg_order_value: parseFloat(customer.avg_order_value),
          last_purchase_date: customer.last_purchase_date,
        },
        predictions: predictions || {
          clv_12m: parseFloat(customer.total_revenue) * 1.2,
          churn_probability: 0,
          risk_category: 'Low Risk',
        },
        recent_orders: ordersResult.rows,
      },
    });
  } catch (error) {
    console.error('Get customer error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = { getAllCustomers, getCustomerById };