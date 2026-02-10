import React, { useState } from 'react';

const Reports: React.FC = () => {
  const [reports] = useState([
    { id: 1, title: 'Daily Flood Report', date: '2024-01-15', status: 'Generated' },
    { id: 2, title: 'Weekly Analysis', date: '2024-01-14', status: 'Pending' },
    { id: 3, title: 'Monthly Summary', date: '2024-01-10', status: 'Generated' },
  ]);

  return (
    <div className="reports-page">
      <h1>Reports</h1>
      
      <div className="reports-actions">
        <button className="btn btn-primary">Generate New Report</button>
        <select className="form-select">
          <option>All Reports</option>
          <option>Daily</option>
          <option>Weekly</option>
          <option>Monthly</option>
        </select>
      </div>

      <div className="reports-list">
        {reports.map(report => (
          <div key={report.id} className="report-card">
            <div className="report-info">
              <h4>{report.title}</h4>
              <p>Date: {report.date}</p>
              <span className={`status-badge status-${report.status.toLowerCase()}`}>
                {report.status}
              </span>
            </div>
            <div className="report-actions">
              <button className="btn btn-sm">View</button>
              <button className="btn btn-sm">Download</button>
              <button className="btn btn-sm">Share</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Reports;