// GET /api/v1/customers
const getAllCustomers = async (req, res) => {
  try {
    const { page = 1, limit = 20, segment, search } = req.query;

    const customers = [
      {
        customer_id: 'c001', first_name: 'John', last_name: 'Doe',
        email: 'john@example.com', city: 'New York', country: 'USA',
        signup_date: '2024-01-15', current_segment: 'Champion',
        total_orders: 42, total_revenue: 12450.00, avg_order_value: 296.43,
        last_purchase_date: '2024-06-10',
      },
      {
        customer_id: 'c002', first_name: 'Jane', last_name: 'Smith',
        email: 'jane@example.com', city: 'London', country: 'UK',
        signup_date: '2024-03-22', current_segment: 'Loyal',
        total_orders: 28, total_revenue: 8930.00, avg_order_value: 318.93,
        last_purchase_date: '2024-06-08',
      },
      {
        customer_id: 'c003', first_name: 'Bob', last_name: 'Johnson',
        email: 'bob@example.com', city: 'Toronto', country: 'Canada',
        signup_date: '2023-11-05', current_segment: 'At Risk',
        total_orders: 15, total_revenue: 4200.00, avg_order_value: 280.00,
        last_purchase_date: '2024-04-30',
      },
    ];

    res.json({
      status: 'success',
      data: customers,
      pagination: { page: parseInt(page), limit: parseInt(limit), total: customers.length, pages: 1 },
    });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

// GET /api/v1/customers/:id
const getCustomerById = async (req, res) => {
  try {
    const { id } = req.params;

    const customer = {
      customer_id: id, first_name: 'John', last_name: 'Doe',
      email: 'john@example.com', city: 'New York', state: 'NY', country: 'USA',
      signup_date: '2024-01-15', acquisition_channel: 'Organic',
      current_segment: 'Champion', is_active: true,
      scorecard: {
        total_orders: 42, total_revenue: 12450.00, avg_order_value: 296.43,
        purchase_frequency: 8.4, days_since_last_purchase: 3, customer_lifetime_days: 150,
      },
      predictions: {
        clv_12_months: 15420.00, churn_probability: 0.08, predicted_next_purchase_days: 7,
      },
      recent_orders: [
        { order_id: 'ord-001', date: '2024-06-10', amount: 345.00, status: 'Completed' },
        { order_id: 'ord-002', date: '2024-06-03', amount: 210.00, status: 'Completed' },
        { order_id: 'ord-003', date: '2024-05-28', amount: 520.00, status: 'Completed' },
      ],
    };

    res.json({ status: 'success', data: customer });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = { getAllCustomers, getCustomerById };