import { io } from 'socket.io-client';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './pages/Login';
import Layout from './components/Layout';
import KPICards from './components/KPICards';
import Customers from './pages/Customers';
import Analytics from './pages/Analytics';
import Predictions from './pages/Predictions';
import Scenarios from './pages/Scenarios';

function App() {
  const { token } = useSelector((state) => state.auth);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={!token ? <Login /> : <Navigate to="/dashboard" />} />
        <Route path="/dashboard" element={token ? <Dashboard /> : <Navigate to="/login" />} />
        <Route path="/customers" element={token ? <Customers /> : <Navigate to="/login" />} />
        <Route path="/analytics" element={token ? <Analytics /> : <Navigate to="/login" />} />
        <Route path="/predictions" element={token ? <Predictions /> : <Navigate to="/login" />} />
        <Route path="/scenarios" element={token ? <Scenarios /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}

function Dashboard() {
  const { user } = useSelector((state) => state.auth);
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    axios.get('http://localhost:3001/api/v1/dashboard/summary', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setStats(res.data.data)).catch(console.error);
  }, []);

  useEffect(() => {
  const socket = io('http://localhost:3001');
  
  socket.on('customer_events', (event) => {
    setEvents(prev => [{ type: 'event', ...event }, ...prev].slice(0, 10));
  });
  
  socket.on('orders', (order) => {
    setEvents(prev => [{ type: 'order', ...order }, ...prev].slice(0, 10));
  });
  
  socket.on('alerts', (alert) => {
    setEvents(prev => [{ type: 'alert', ...alert }, ...prev].slice(0, 10));
  });
  
  return () => socket.disconnect();
}, []);

  const kpiData = stats ? [
    { title: 'Total Revenue', value: `$${((stats.total_revenue || 0) / 1000).toFixed(0)}K`, change: '+12.5%', color: 'green' },
    { title: 'Total Customers', value: stats.total_customers || 0, change: '+8.3%', color: 'blue' },
    { title: 'Total Orders', value: stats.total_orders || 0, change: '+8.1%', color: 'purple' },
    { title: 'Avg Order Value', value: `$${Number(stats.avg_order_value || 0).toFixed(2)}`, change: '+5.3%', color: 'green' },
  ] : null;

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome back, {user?.first_name}</p>
      </div>
      
      {kpiData ? <KPICards data={kpiData} /> : <KPICards />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Revenue Overview</h2>
          <p className="text-gray-400">Monthly revenue data available in Analytics →</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Live Customer Events</h2>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {events.length === 0 && <p className="text-gray-500">Waiting for events...</p>}
            {events.map((event, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-750 rounded p-2 text-sm">
                <span className="text-gray-300">{event.event_type}</span>
                <span className="text-gray-500">Customer #{event.customer_id}</span>
                <span className="text-green-400">${event.amount}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;