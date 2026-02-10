import React from 'react';

const SystemStatusPage: React.FC = () => {
  const systems = [
    { name: 'ML Prediction Engine', status: 'active', lastCheck: '2 min ago' },
    { name: 'Weather API', status: 'active', lastCheck: '5 min ago' },
    { name: 'Satellite Data', status: 'warning', lastCheck: '10 min ago' },
    { name: 'Database', status: 'active', lastCheck: '1 min ago' },
    { name: 'Notification System', status: 'active', lastCheck: '3 min ago' },
  ];

  return (
    <div className="system-status-page">
      <h1>System Status</h1>
      
      <div className="system-overview">
        <div className="overview-card">
          <h3>Overall Status</h3>
          <div className="status-indicator status-good">
            Operational
          </div>
        </div>
        
        <div className="overview-card">
          <h3>Uptime</h3>
          <div className="uptime">99.8%</div>
        </div>
      </div>

      <div className="systems-list">
        {systems.map((system, index) => (
          <div key={index} className="system-item">
            <div className="system-info">
              <h4>{system.name}</h4>
              <p>Last checked: {system.lastCheck}</p>
            </div>
            <div className={`status-badge status-${system.status}`}>
              {system.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SystemStatusPage;