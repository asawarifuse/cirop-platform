import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { customerAPI } from '../services/api';

function Customers() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await customerAPI.getAll({ limit: 50 });
      setCustomers(response.data.data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const segments = ['All', 'Champions', 'Loyal Customers', 'Potential Loyalists', 'At Risk', 'Lost Customers'];

  const segmentColors = {
    'Champions': 'bg-yellow-500/20 text-yellow-400',
    'Loyal Customers': 'bg-green-500/20 text-green-400',
    'Potential Loyalists': 'bg-blue-500/20 text-blue-400',
    'At Risk': 'bg-orange-500/20 text-orange-400',
    'Lost Customers': 'bg-red-500/20 text-red-400',
  };

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Customers</h1>
        <p className="text-gray-400 mt-1">Manage and analyze your customer base</p>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6 flex-wrap">
        {segments.map((seg) => (
          <button
            key={seg}
            className={`px-4 py-2 rounded-lg text-sm transition ${
              seg === 'All'
                ? 'bg-gray-700 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
            }`}
          >
            {seg}
          </button>
        ))}
        <input
          type="text"
          placeholder="Search customers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="ml-auto px-4 py-2 rounded-lg bg-gray-800 text-white border border-gray-700 focus:border-blue-500 focus:outline-none w-64"
        />
      </div>

      {/* Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left p-4 text-gray-400 text-sm font-medium">Customer</th>
              <th className="text-left p-4 text-gray-400 text-sm font-medium">City</th>
              <th className="text-left p-4 text-gray-400 text-sm font-medium">Country</th>
              <th className="text-left p-4 text-gray-400 text-sm font-medium">Segment</th>
              <th className="text-right p-4 text-gray-400 text-sm font-medium">Orders</th>
              <th className="text-right p-4 text-gray-400 text-sm font-medium">Revenue</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan="6" className="text-center p-8 text-gray-500">Loading...</td>
              </tr>
            ) : (
              customers.map((customer) => (
                <tr key={customer.customer_id} className="border-b border-gray-700/50 hover:bg-gray-750 transition">
                  <td className="p-4">
                    <p className="text-white font-medium">{customer.first_name} {customer.last_name}</p>
                    <p className="text-gray-500 text-sm">{customer.email}</p>
                  </td>
                  <td className="p-4 text-gray-300">{customer.city}</td>
                  <td className="p-4 text-gray-300">{customer.country}</td>
                  <td className="p-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${segmentColors[customer.current_segment] || 'bg-gray-500/20 text-gray-400'}`}>
                      {customer.current_segment || 'Unassigned'}
                    </span>
                  </td>
                  <td className="p-4 text-right text-gray-300">{customer.total_orders || '-'}</td>
                  <td className="p-4 text-right text-green-400 font-medium">
                    {customer.total_revenue ? `$${customer.total_revenue.toLocaleString()}` : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center mt-4 text-gray-400 text-sm">
        <span>Showing {customers.length} customers</span>
        <div className="flex gap-2">
          <button className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 transition">Previous</button>
          <button className="px-3 py-1 rounded bg-gray-800 hover:bg-gray-700 transition">Next</button>
        </div>
      </div>
    </Layout>
  );
}

export default Customers;