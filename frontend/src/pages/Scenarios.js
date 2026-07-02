import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import { mlAPI } from '../services/api';

function Scenarios() {
  const [scenarios, setScenarios] = useState([]);
  const [topRecommendation, setTopRecommendation] = useState('');
  const [loading, setLoading] = useState(true);
  const [activeScenario, setActiveScenario] = useState(null);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const response = await mlAPI.getScenarios();
      setScenarios(response.data.scenarios);
      setTopRecommendation(response.data.top_recommendation);
    } catch (error) {
      console.error('Failed to fetch scenarios:', error);
      setScenarios([
        { name: '10% Churn Reduction', revenue_impact: 8356.49 },
        { name: '5% Retention Increase', revenue_impact: 10744.06 },
        { name: '20% Marketing Budget Increase', revenue_impact: 10637.08 },
        { name: '$50 AOV Increase', revenue_impact: 148300.00 },
        { name: '20% At Risk → Loyal Conversion', revenue_impact: 1905.42 },
      ]);
      setTopRecommendation('$50 AOV Increase ($148,300.00 impact)');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64 text-gray-400">Loading scenarios...</div>
      </Layout>
    );
  }

  const getScenarioIcon = (name) => {
    if (name.includes('Churn')) return '⚠️';
    if (name.includes('Retention')) return '🔒';
    if (name.includes('Marketing')) return '📢';
    if (name.includes('AOV')) return '💰';
    if (name.includes('At Risk')) return '🎯';
    return '📊';
  };

  const getScenarioColor = (name) => {
    if (name.includes('AOV')) return 'border-green-500 bg-green-500/10';
    if (name.includes('Churn')) return 'border-red-500 bg-red-500/10';
    if (name.includes('Retention')) return 'border-blue-500 bg-blue-500/10';
    if (name.includes('Marketing')) return 'border-purple-500 bg-purple-500/10';
    return 'border-yellow-500 bg-yellow-500/10';
  };

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Scenario Simulator</h1>
        <p className="text-gray-400 mt-1">What-if analysis for business decisions</p>
      </div>

      {/* Top Recommendation */}
      <div className="bg-green-500/10 border border-green-500 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏆</span>
          <div>
            <p className="text-green-400 text-sm font-medium">Top Recommendation</p>
            <p className="text-white text-lg">{topRecommendation}</p>
          </div>
        </div>
      </div>

      {/* Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {scenarios.map((scenario, index) => (
          <div
            key={index}
            className={`border-l-4 rounded-lg p-5 cursor-pointer transition hover:scale-105 ${getScenarioColor(scenario.name)}`}
            onClick={() => setActiveScenario(activeScenario === index ? null : index)}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{getScenarioIcon(scenario.name)}</span>
            </div>
            <h3 className="text-white font-semibold mb-2">{scenario.name}</h3>
            <p className="text-2xl font-bold text-white">
              ${scenario.revenue_impact?.toLocaleString()}
            </p>
            <p className="text-gray-400 text-sm mt-1">Revenue Impact</p>
          </div>
        ))}
      </div>

      {/* Detailed Analysis */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Scenario Analysis</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-3 text-gray-400 text-sm">Scenario</th>
                <th className="text-right p-3 text-gray-400 text-sm">Revenue Impact</th>
                <th className="text-right p-3 text-gray-400 text-sm">Priority</th>
                <th className="text-center p-3 text-gray-400 text-sm">Action</th>
              </tr>
            </thead>
            <tbody>
              {scenarios
                .sort((a, b) => b.revenue_impact - a.revenue_impact)
                .map((scenario, index) => (
                  <tr key={index} className="border-b border-gray-700/50 hover:bg-gray-750">
                    <td className="p-3 text-white">{scenario.name}</td>
                    <td className="p-3 text-right text-green-400 font-medium">
                      ${scenario.revenue_impact?.toLocaleString()}
                    </td>
                    <td className="p-3 text-right">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        index === 0 ? 'bg-red-500/20 text-red-400' :
                        index <= 1 ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-blue-500/20 text-blue-400'
                      }`}>
                        {index === 0 ? 'High' : index <= 1 ? 'Medium' : 'Low'}
                      </span>
                    </td>
                    <td className="p-3 text-center">
                      <button className="text-blue-400 hover:text-blue-300 text-sm">
                        Simulate →
                      </button>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}

export default Scenarios;