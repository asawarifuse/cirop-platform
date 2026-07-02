import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
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

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome back, {user?.first_name}</p>
      </div>
      
      <KPICards />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Revenue Overview</h2>
          <div className="h-48 flex items-center justify-center text-gray-500">
            Revenue chart loading...
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-lg font-semibold text-white mb-4">Customer Segments</h2>
          <div className="h-48 flex items-center justify-center text-gray-500">
            Segments chart loading...
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;