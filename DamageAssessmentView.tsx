import React, { useState } from 'react';

const DamageAssessmentView: React.FC = () => {
  const [reportId, setReportId] = useState<string>('');
  const [report, setReport] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);

  const handleCreateReport = async () => {
    const res = await fetch('/api/relief/damage', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disaster_id: 'DIS001', location: { lat: 26.0, lon: 74.0 }, area_sq_km: 25 })
    });
    const data = await res.json();
    if (data.success) {
      setReportId(data.report.id);
      setReport(data.report);
    }
  };

  const handleAssessStructural = async () => {
    const res = await fetch(`/api/relief/damage/${reportId}/assess`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: 'structural', buildings_inspected: 200, collapsed: 12, partial_damage: 35, minor_damage: 60 })
    });
    const data = await res.json();
    if (data.success) setReport({ ...report, assessments: { ...report?.assessments, structural: data.assessment } });
  };

  const handleGetSummary = async () => {
    if (!reportId) return;
    const res = await fetch(`/api/relief/damage/${reportId}/summary`);
    const data = await res.json();
    if (data.success) setSummary(data.summary);
  };

  const severityColors: Record<string, string> = { critical: '#F44336', severe: '#FF9800', moderate: '#FFC107', minor: '#4CAF50', unknown: '#888' };

  return (
    <div className="damage-assessment">
      <h2>Damage Assessment</h2>
      <button onClick={handleCreateReport} style={{ padding: '8px 16px', backgroundColor: '#9C27B0', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', marginBottom: 16 }}>
        Create New Report
      </button>
      {report && (
        <div style={{ border: '1px solid #333', borderRadius: 8, padding: 16, marginBottom: 16 }}>
          <h3>Report: {report.id}</h3>
          <p>Status: {report.status} | Area: {report.affected_area_sq_km} km²</p>
          <button onClick={handleAssessStructural} style={{ padding: '6px 12px', backgroundColor: '#7B1FA2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', marginRight: 8 }}>
            Assess Structural Damage
          </button>
          <button onClick={handleGetSummary} style={{ padding: '6px 12px', backgroundColor: '#5C6BC0', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Generate Summary
          </button>
        </div>
      )}
      {summary && (
        <div style={{ border: '1px solid #333', borderRadius: 8, padding: 16, borderLeft: `4px solid ${severityColors[summary.severity] || '#888'}` }}>
          <h3>Summary</h3>
          <div style={{ fontSize: '1.2em', fontWeight: 'bold', color: severityColors[summary.severity] || '#888' }}>
            Severity: {summary.severity?.toUpperCase()} (Score: {summary.composite_score})
          </div>
          <p>Worst Category: {summary.worst_category?.category} ({summary.worst_category?.score})</p>
          <p>Recommendation: {summary.recommendation}</p>
        </div>
      )}
    </div>
  );
};

export default DamageAssessmentView;
