import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import KPICards from '../components/KPICards';
import { orderAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

function Analytics() {
  const [revenue, setRevenue] = useState(null);
  const [products, setProducts] = useState(null);
  const [frequency, setFrequency] = useState(null);
  const [aov, setAOV] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [revRes, prodRes, freqRes, aovRes] = await Promise.all([
        orderAPI.getRevenue(),
        orderAPI.getProducts(),
        orderAPI.getFrequency(),
        orderAPI.getAOV(),
      ]);
      setRevenue(revRes.data.data || revRes.data);
      setProducts(prodRes.data.data || prodRes.data);
      setFrequency(freqRes.data.data || freqRes.data);
      setAOV(aovRes.data.data || aovRes.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64 text-gray-400">Loading analytics...</div>
      </Layout>
    );
  }

  const totalRevenue = revenue?.total_revenue || 0;
  const overallAOV = aov?.overall_aov || 0;
  const growthPct = revenue?.revenue_growth_pct || 0;

  const kpiData = [
    { title: 'Total Revenue', value: `$${(totalRevenue / 1000).toFixed(0)}K`, change: `+${growthPct}%`, color: 'green' },
    { title: 'Avg Order Value', value: `$${Number(overallAOV).toFixed(2)}`, change: '+5.3%', color: 'blue' },
    { title: 'Total Orders', value: '2,966', change: '+8.1%', color: 'purple' },
    { title: 'Products Sold', value: '50', change: '+3.2%', color: 'green' },
  ];

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-gray-400 mt-1">Revenue, products, and order insights</p>
      </div>

      <KPICards data={kpiData} />

      {/* Revenue Trend */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">Monthly Revenue</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={revenue?.monthly_revenue || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} />
            <YAxis stroke="#9CA3AF" fontSize={12} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              labelStyle={{ color: '#fff' }}
            />
            <Bar dataKey="revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Revenue ($)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Revenue by Category */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Revenue by Category</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={revenue?.revenue_by_category || []}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="revenue"
                nameKey="category"
                label={({ category, pct }) => `${category} (${pct}%)`}
              >
                {(revenue?.revenue_by_category || []).map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* AOV by Segment */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">AOV by Customer Segment</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={aov?.aov_by_segment || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" fontSize={12} />
              <YAxis dataKey="segment" type="category" stroke="#9CA3AF" fontSize={12} width={120} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              />
              <Bar dataKey="aov" fill="#10B981" radius={[0, 4, 4, 0]} name="Avg Order Value ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Frequency Distribution */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <h2 className="text-lg font-semibold text-white mb-4">Purchase Frequency Distribution</h2>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={frequency?.frequency_distribution || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="range" stroke="#9CA3AF" fontSize={12} />
            <YAxis stroke="#9CA3AF" fontSize={12} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
            />
            <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Customers" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Top Products */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Top Products</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-3 text-gray-400 text-sm">#</th>
                <th className="text-left p-3 text-gray-400 text-sm">Product</th>
                <th className="text-right p-3 text-gray-400 text-sm">Revenue</th>
                <th className="text-right p-3 text-gray-400 text-sm">Units Sold</th>
                <th className="text-right p-3 text-gray-400 text-sm">Rating</th>
              </tr>
            </thead>
            <tbody>
              {(products?.top_products || []).map((product, index) => (
                <tr key={index} className="border-b border-gray-700/50">
                  <td className="p-3 text-gray-400">{index + 1}</td>
                  <td className="p-3 text-white">{product.product}</td>
                  <td className="p-3 text-right text-green-400">${(product.revenue || 0).toLocaleString()}</td>
                  <td className="p-3 text-right text-gray-300">{product.units_sold}</td>
                  <td className="p-3 text-right text-yellow-400">{'⭐'.repeat(Math.round(product.avg_rating || 4))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}

export default Analytics;