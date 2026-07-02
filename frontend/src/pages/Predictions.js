import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { mlAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#EF4444', '#F59E0B', '#3B82F6', '#10B981'];

function Predictions() {
  const [segments, setSegments] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [churnData, setChurnData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [segRes, foreRes, churnRes] = await Promise.all([
        mlAPI.getSegments(),
        mlAPI.getForecast(),
        mlAPI.getChurnSummary(),
      ]);
      setSegments(segRes.data);
      setForecast(foreRes.data);
      setChurnData(churnRes.data);
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64 text-gray-400">Loading predictions...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Predictions</h1>
        <p className="text-gray-400 mt-1">ML-powered customer insights and forecasts</p>
      </div>

      {/* Revenue Forecast */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Next 30 Days</p>
          <p className="text-white text-2xl font-bold mt-1">${(forecast?.next_30_days / 1000).toFixed(1)}K</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Next 90 Days</p>
          <p className="text-white text-2xl font-bold mt-1">${(forecast?.next_90_days / 1000).toFixed(1)}K</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Next 365 Days</p>
          <p className="text-white text-2xl font-bold mt-1">${(forecast?.next_365_days / 1000).toFixed(1)}K</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">YoY Growth</p>
          <p className="text-green-400 text-2xl font-bold mt-1">+{forecast?.growth_pct}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Customer Segments */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Customer Segments</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={segments}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="customer_count"
                nameKey="segment"
                label={({ segment, customer_count }) => `${segment}: ${customer_count}`}
              >
                {segments.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Churn Risk Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Churn Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={churnData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="risk_category" stroke="#9CA3AF" fontSize={12} />
              <YAxis stroke="#9CA3AF" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '8px' }}
              />
              <Bar dataKey="customers" fill="#EF4444" radius={[4, 4, 0, 0]} name="Customers" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment Details Table */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Segment Details</h2>
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left p-3 text-gray-400 text-sm">Segment</th>
              <th className="text-right p-3 text-gray-400 text-sm">Customers</th>
              <th className="text-right p-3 text-gray-400 text-sm">Avg Revenue</th>
              <th className="text-right p-3 text-gray-400 text-sm">Total Revenue</th>
            </tr>
          </thead>
          <tbody>
            {segments.map((seg, index) => (
              <tr key={index} className="border-b border-gray-700/50">
                <td className="p-3 text-white">{seg.segment}</td>
                <td className="p-3 text-right text-gray-300">{seg.customer_count}</td>
                <td className="p-3 text-right text-gray-300">${seg.avg_revenue?.toLocaleString()}</td>
                <td className="p-3 text-right text-green-400">
                  ${(seg.customer_count * seg.avg_revenue).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}

export default Predictions;