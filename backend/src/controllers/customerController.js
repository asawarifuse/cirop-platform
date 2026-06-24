const mlApiService = require('../services/mlApiService');

const getAllCustomers = async (req, res) => {
  try {
    const { page = 1, limit = 20 } = req.query;

    const customers = [
      { customer_id: 1, first_name: 'James', last_name: 'Smith', email: 'customer0@example.com', city: 'New York', country: 'USA' },
      { customer_id: 2, first_name: 'Mary', last_name: 'Johnson', email: 'customer1@example.com', city: 'Los Angeles', country: 'USA' },
      { customer_id: 3, first_name: 'Robert', last_name: 'Williams', email: 'customer2@example.com', city: 'Chicago', country: 'USA' },
      { customer_id: 4, first_name: 'Patricia', last_name: 'Brown', email: 'customer3@example.com', city: 'Houston', country: 'USA' },
      { customer_id: 5, first_name: 'John', last_name: 'Jones', email: 'customer4@example.com', city: 'Phoenix', country: 'USA' },
    ];

    res.json({
      status: 'success',
      data: customers,
      pagination: { page: parseInt(page), limit: parseInt(limit), total: 500, pages: 100 },
    });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

const getCustomerById = async (req, res) => {
  try {
    const { id } = req.params;

    // Fetch real predictions from ML API
    const predictions = await mlApiService.getCustomerPrediction(id);

    const customer = {
      customer_id: parseInt(id),
      first_name: 'James',
      last_name: 'Smith',
      email: `customer${id}@example.com`,
      city: 'New York',
      state: 'NY',
      country: 'USA',
      signup_date: '2023-06-15',
      acquisition_channel: 'Organic',
      current_segment: predictions?.segment || 'Unknown',
      is_active: true,
      scorecard: {
        total_orders: 12,
        total_revenue: 2450.00,
        avg_order_value: 204.17,
        purchase_frequency: 2.4,
        days_since_last_purchase: 45,
        customer_lifetime_days: 560,
      },
      predictions: {
        clv_12_months: predictions?.clv_12m || 0,
        churn_probability: predictions?.churn_probability || 0,
        risk_category: predictions?.risk_category || 'Unknown',
      },
      recent_orders: [
        { order_id: 'ord-001', date: '2024-12-20', amount: 345.00, status: 'Completed' },
        { order_id: 'ord-002', date: '2024-12-10', amount: 210.00, status: 'Completed' },
        { order_id: 'ord-003', date: '2024-11-28', amount: 520.00, status: 'Completed' },
      ],
    };

    res.json({ status: 'success', data: customer });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = { getAllCustomers, getCustomerById };