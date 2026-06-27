function KPICards({ data }) {
  const defaultCards = [
    { title: 'Total Revenue', value: '$501,972', change: '+12.5%', color: 'green' },
    { title: 'Total Customers', value: '500', change: '+8.3%', color: 'blue' },
    { title: 'Churn Rate', value: '27.8%', change: '-2.1%', color: 'red' },
    { title: 'Avg CLV', value: '$589.81', change: '+5.7%', color: 'purple' },
  ];

  const cards = data || defaultCards;

  const colorMap = {
    green: 'border-green-500 bg-green-500/10',
    blue: 'border-blue-500 bg-blue-500/10',
    red: 'border-red-500 bg-red-500/10',
    purple: 'border-purple-500 bg-purple-500/10',
  };

  const changeColorMap = {
    green: 'text-green-400',
    blue: 'text-blue-400',
    red: 'text-red-400',
    purple: 'text-purple-400',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`border-l-4 rounded-lg p-4 ${colorMap[card.color] || colorMap.blue}`}
        >
          <p className="text-gray-400 text-sm">{card.title}</p>
          <p className="text-white text-2xl font-bold mt-1">{card.value}</p>
          <p className={`text-sm mt-2 ${changeColorMap[card.color] || changeColorMap.blue}`}>
            {card.change} vs last period
          </p>
        </div>
      ))}
    </div>
  );
}

export default KPICards;