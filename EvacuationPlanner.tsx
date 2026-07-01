import React, { useState, useEffect } from 'react';

interface Shelter { id: string; name: string; capacity: number; occupied: number; available: number; fill_pct: number; }

const EvacuationPlanner: React.FC = () => {
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [originLat, setOriginLat] = useState('26.2389');
  const [originLon, setOriginLon] = useState('73.0243');
  const [population, setPopulation] = useState('500');
  const [planResult, setPlanResult] = useState<any>(null);

  useEffect(() => {
    fetch('/api/relief/evacuation/shelters').then(r => r.json()).then(d => {
      if (d.success) setShelters(d.shelters);
    });
  }, []);

  const handlePlanEvacuation = async () => {
    const res = await fetch('/api/relief/evacuation/plan', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat: parseFloat(originLat), lon: parseFloat(originLon), population: parseInt(population) })
    });
    const data = await res.json();
    setPlanResult(data);
  };

  return (
    <div className="evacuation-planner">
      <h2>Evacuation Route Planner</h2>
      <div className="plan-controls" style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        <input placeholder="Latitude" value={originLat} onChange={e => setOriginLat(e.target.value)} style={{ padding: 8, borderRadius: 4, border: '1px solid #555', backgroundColor: '#1a1a2e', color: '#fff' }} />
        <input placeholder="Longitude" value={originLon} onChange={e => setOriginLon(e.target.value)} style={{ padding: 8, borderRadius: 4, border: '1px solid #555', backgroundColor: '#1a1a2e', color: '#fff' }} />
        <input placeholder="Population" value={population} onChange={e => setPopulation(e.target.value)} style={{ padding: 8, borderRadius: 4, border: '1px solid #555', backgroundColor: '#1a1a2e', color: '#fff' }} />
        <button onClick={handlePlanEvacuation} style={{ padding: '8px 16px', backgroundColor: '#FF9800', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Plan Evacuation</button>
      </div>

      {planResult?.success && (
        <div className="plan-result" style={{ border: '1px solid #4CAF50', borderRadius: 8, padding: 16, marginBottom: 16 }}>
          <h3>Evacuation Plan</h3>
          <p><strong>Destination:</strong> {planResult.evacuation_plan.destination.name}</p>
          <p><strong>Distance:</strong> {planResult.evacuation_plan.total_distance_km} km</p>
          <p><strong>Estimated Time:</strong> {planResult.evacuation_plan.estimated_time_minutes} min</p>
          <p><strong>Vehicles Needed:</strong> {planResult.evacuation_plan.vehicles_needed}</p>
        </div>
      )}

      <h3>Available Shelters</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 12 }}>
        {shelters.map(s => (
          <div key={s.id} style={{ border: '1px solid #333', borderRadius: 8, padding: 12 }}>
            <h4 style={{ margin: 0 }}>{s.name}</h4>
            <div>Capacity: {s.available}/{s.capacity}</div>
            <div style={{ height: 4, backgroundColor: '#333', borderRadius: 2, marginTop: 4 }}>
              <div style={{ height: '100%', width: `${s.fill_pct}%`, backgroundColor: s.fill_pct > 80 ? '#F44336' : s.fill_pct > 50 ? '#FFC107' : '#4CAF50', borderRadius: 2 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EvacuationPlanner;
