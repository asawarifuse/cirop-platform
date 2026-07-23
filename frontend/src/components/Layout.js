import { useTheme } from '../context/ThemeContext';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../store/authSlice';
import { useNavigate, NavLink } from 'react-router-dom';

function Layout({ children }) {
  const { darkMode, toggleTheme } = useTheme();
  const { user } = useSelector((state) => state.auth);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/customers', label: 'Customers', icon: '👥' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/predictions', label: 'Predictions', icon: '🤖' },
    { path: '/scenarios', label: 'Scenarios', icon: '🔮' },
  ];

  return (
    <div className={`flex h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-100'}`}>
      {/* Mobile hamburger */}
      <button
        className={`lg:hidden fixed top-4 left-4 z-50 p-2 rounded ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800 shadow'}`}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <div className={`w-64 border-r flex flex-col fixed lg:relative h-full z-40 transition-transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'} ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
        <div className={`p-4 border-b flex items-center justify-between ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div>
            <h1 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-900'}`}>CIROP</h1>
            <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>Intelligence Platform</p>
          </div>
          <button onClick={toggleTheme} className="text-xl hover:scale-110 transition">
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        
        <nav className="flex-1 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg mb-1 transition ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : darkMode 
                      ? 'text-gray-400 hover:bg-gray-700 hover:text-white' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={`p-4 border-t ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-900'}`}>{user?.first_name} {user?.last_name}</p>
              <p className={`text-xs capitalize ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{user?.role}</p>
            </div>
            <button onClick={handleLogout} className="text-gray-400 hover:text-red-400 text-sm">Logout</button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 overflow-auto pt-14 lg:pt-0 ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
        <div className="p-4 md:p-6">
          {children}
        </div>
      </div>
    </div>
  );
}

export default Layout;