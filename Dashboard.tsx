import React from 'react';
import MetricCard from '../components/MetricCard';
import SevenDayRainfallChart from '../components/SevenDayRainfallChart';
import RealTimeMonitor from '../components/RealTimeMonitor';
import SystemStatus from '../components/SystemStatus';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      <div className="metrics-grid">
        <MetricCard 
          title="Flood Risk Level" 
          value="Medium" 
          unit=""
          trend="up"
        />
        <MetricCard 
          title="Current Rainfall" 
          value="12.5" 
          unit="mm"
          trend="down"
        />
        <MetricCard 
          title="Soil Moisture" 
          value="65%" 
          unit=""
          trend="stable"
        />
        <MetricCard 
          title="Water Level" 
          value="3.2" 
          unit="m"
          trend="up"
        />
      </div>

      <div className="charts-section">
        <SevenDayRainfallChart />
        <RealTimeMonitor />
      </div>

      <SystemStatus />
    </div>
  );
};

export default Dashboard;