import React, { useState, useEffect } from 'react';

interface InventoryItem {
  total: number; allocated: number; reserved: number; available: number; unit: string; usage_percent: number;
}

interface Depot {
  id: string; name: string; lat: number; lon: number; capacity: number; current_load: number; status: string; current_load_pct: number;
}

const ResourceManagement: React.FC = () => {
  const [inventory, setInventory] = useState<Record<string, InventoryItem>>({});
  const [depots, setDepots] = useState<Depot[]>([]);
  const [allocResult, setAllocResult] = useState<string>('');

  useEffect(() => {
    fetch('/api/relief/resources').then(r => r.json()).then(d => {
      if (d.success) { setInventory(d.inventory); setDepots(d.depots); }
    });
  }, []);

  const handleAllocate = async () => {
    const res = await fetch('/api/relief/resources/allocate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource_type: 'food', quantity: 500, disaster_id: 'DIS001', location: { lat: 26.0, lon: 74.0 } })
    });
    const data = await res.json();
    setAllocResult(data.success ? 'Allocation successful!' : `Error: ${data.error}`);
  };

  return (
    <div className="resource-management">
      <h2>Resource Management</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12, marginBottom: 16 }}>
        {Object.entries(inventory).map(([key, val]) => (
          <div key={key} style={{ border: '1px solid #333', borderRadius: 8, padding: 12 }}>
            <h4 style={{ margin: 0, textTransform: 'capitalize' }}>{key}</h4>
            <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{val.available} <span style={{ fontSize: '0.6em', color: '#888' }}>{val.unit}</span></div>
            <div style={{ fontSize: '0.8em', color: '#888' }}>Used: {val.usage_percent}%</div>
            <div style={{ height: 4, backgroundColor: '#333', borderRadius: 2, marginTop: 4 }}>
              <div style={{ height: '100%', width: `${val.usage_percent}%`, backgroundColor: val.usage_percent > 80 ? '#F44336' : val.usage_percent > 50 ? '#FFC107' : '#4CAF50', borderRadius: 2 }} />
            </div>
          </div>
        ))}
      </div>
      <button onClick={handleAllocate} style={{ padding: '8px 16px', backgroundColor: '#2196F3', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>Allocate Food (500 units)</button>
      {allocResult && <p style={{ marginTop: 8 }}>{allocResult}</p>}
      <h3 style={{ marginTop: 16 }}>Depot Status</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 12 }}>
        {depots.map(d => (
          <div key={d.id} style={{ border: '1px solid #333', borderRadius: 8, padding: 12 }}>
            <h4 style={{ margin: 0 }}>{d.name}</h4>
            <div>Status: {d.status}</div>
            <div>Load: {d.current_load_pct}%</div>
            <div style={{ height: 4, backgroundColor: '#333', borderRadius: 2, marginTop: 4 }}>
              <div style={{ height: '100%', width: `${d.current_load_pct}%`, backgroundColor: d.current_load_pct > 80 ? '#F44336' : '#4CAF50', borderRadius: 2 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResourceManagement;
