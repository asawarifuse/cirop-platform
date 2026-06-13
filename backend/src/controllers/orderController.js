// GET /api/v1/orders/analytics/revenue
const getRevenueAnalytics = async (req, res) => {
  try {
    const data = {
      total_revenue: 284650.00,
      revenue_growth_pct: 12.5,
      monthly_revenue: [
        { month: '2024-01', revenue: 42000, orders: 145 },
        { month: '2024-02', revenue: 38500, orders: 132 },
        { month: '2024-03', revenue: 45600, orders: 158 },
        { month: '2024-04', revenue: 51200, orders: 172 },
        { month: '2024-05', revenue: 48900, orders: 165 },
        { month: '2024-06', revenue: 58450, orders: 198 },
      ],
      revenue_by_category: [
        { category: 'Electronics', revenue: 98500, pct: 34.6 },
        { category: 'Clothing', revenue: 72300, pct: 25.4 },
        { category: 'Home & Garden', revenue: 54800, pct: 19.3 },
        { category: 'Sports', revenue: 35200, pct: 12.4 },
        { category: 'Books', revenue: 23850, pct: 8.3 },
      ],
    };

    res.json({ status: 'success', data });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

// GET /api/v1/orders/analytics/products
const getProductPerformance = async (req, res) => {
  try {
    const data = {
      top_products: [
        { product: 'Wireless Headphones', revenue: 42500, units_sold: 850, avg_rating: 4.5 },
        { product: 'Running Shoes', revenue: 38100, units_sold: 635, avg_rating: 4.3 },
        { product: 'Coffee Maker', revenue: 29400, units_sold: 420, avg_rating: 4.7 },
        { product: 'Yoga Mat', revenue: 18200, units_sold: 910, avg_rating: 4.1 },
        { product: 'Desk Lamp', revenue: 15600, units_sold: 520, avg_rating: 4.4 },
      ],
      bottom_products: [
        { product: 'Phone Case', revenue: 3200, units_sold: 160, avg_rating: 3.8 },
        { product: 'USB Cable', revenue: 2800, units_sold: 280, avg_rating: 3.5 },
      ],
    };

    res.json({ status: 'success', data });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

// GET /api/v1/orders/analytics/frequency
const getPurchaseFrequency = async (req, res) => {
  try {
    const data = {
      avg_purchase_interval_days: 28,
      frequency_distribution: [
        { range: 'Weekly', count: 120, pct: 8.5 },
        { range: 'Bi-weekly', count: 245, pct: 17.3 },
        { range: 'Monthly', count: 480, pct: 33.9 },
        { range: 'Quarterly', count: 355, pct: 25.1 },
        { range: 'Yearly', count: 215, pct: 15.2 },
      ],
      avg_order_value_trend: [
        { month: '2024-01', aov: 289.66 },
        { month: '2024-02', aov: 291.67 },
        { month: '2024-03', aov: 288.61 },
        { month: '2024-04', aov: 297.67 },
        { month: '2024-05', aov: 296.36 },
        { month: '2024-06', aov: 295.20 },
      ],
    };

    res.json({ status: 'success', data });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

// GET /api/v1/orders/analytics/aov
const getAverageOrderValue = async (req, res) => {
  try {
    const data = {
      overall_aov: 293.45,
      aov_by_segment: [
        { segment: 'Champions', aov: 385.20 },
        { segment: 'Loyal Customers', aov: 310.50 },
        { segment: 'Potential Loyalists', aov: 265.30 },
        { segment: 'At Risk', aov: 220.80 },
        { segment: 'Lost', aov: 180.40 },
      ],
      aov_by_channel: [
        { channel: 'Organic', aov: 320.50 },
        { channel: 'Paid Search', aov: 280.30 },
        { channel: 'Referral', aov: 345.60 },
        { channel: 'Direct', aov: 275.40 },
        { channel: 'Partner', aov: 310.20 },
      ],
    };

    res.json({ status: 'success', data });
  } catch (error) {
    res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = { getRevenueAnalytics, getProductPerformance, getPurchaseFrequency, getAverageOrderValue };