import React, { useState } from 'react';

const Alerts: React.FC = () => {
  const [alerts] = useState([
    { id: 1, type: 'warning', message: 'Heavy rainfall expected in 2 hours', time: '10:30 AM', area: 'District A' },
    { id: 2, type: 'danger', message: 'River level critical', time: '09:15 AM', area: 'District B' },
    { id: 3, type: 'info', message: 'Moderate flood risk', time: '08:00 AM', area: 'District C' },
  ]);

  return (
    <div className="alerts-page">
      <h1>Alert Management</h1>
      
      <div className="alerts-header">
        <button className="btn btn-primary">Send New Alert</button>
        <button className="btn btn-secondary">Export Alerts</button>
      </div>

      <div className="alerts-list">
        {alerts.map(alert => (
          <div key={alert.id} className={`alert-item alert-${alert.type}`}>
            <div className="alert-content">
              <h4>{alert.message}</h4>
              <p>Area: {alert.area} • Time: {alert.time}</p>
            </div>
            <div className="alert-actions">
              <button className="btn btn-sm">Acknowledge</button>
              <button className="btn btn-sm">Forward</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Alerts;