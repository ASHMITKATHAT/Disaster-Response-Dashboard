import React, { useState, useEffect } from 'react';

interface Contact {
  id: string; name: string; type: string; phone: string; alternate_phone: string | null;
  email: string | null; service_area: string; status: string; priority: number;
}

const EmergencyContacts: React.FC = () => {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [hotlines, setHotlines] = useState<any>(null);
  const [filterType, setFilterType] = useState('');

  useEffect(() => {
    const endpoint = filterType ? `/api/relief/contacts?type=${filterType}` : '/api/relief/contacts';
    fetch(endpoint).then(r => r.json()).then(d => { if (d.success) setContacts(d.contacts); });
    fetch('/api/relief/contacts/hotlines').then(r => r.json()).then(d => { if (d.success) setHotlines(d.hotlines); });
  }, [filterType]);

  const typeColors: Record<string, string> = {
    police: '#1565C0', fire: '#E65100', ambulance: '#2E7D32', hospital: '#00695C',
    disaster_response: '#F44336', military: '#4E342E', ngo: '#6A1B9A', government: '#37474F'
  };

  return (
    <div className="emergency-contacts">
      <h2>Emergency Contacts</h2>

      {hotlines && (
        <div style={{ border: '1px solid #F44336', borderRadius: 8, padding: 16, marginBottom: 16, backgroundColor: 'rgba(244,67,54,0.1)' }}>
          <h3>National Hotlines</h3>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {hotlines.national_hotlines?.map((h: any, i: number) => (
              <div key={i} style={{ textAlign: 'center', padding: '8px 16px', backgroundColor: '#1a1a2e', borderRadius: 8 }}>
                <div style={{ textTransform: 'capitalize', fontSize: '0.8em' }}>{h.type}</div>
                <div style={{ fontSize: '1.3em', fontWeight: 'bold' }}>{h.number}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <select value={filterType} onChange={e => setFilterType(e.target.value)} style={{ padding: 8, borderRadius: 4, border: '1px solid #555', backgroundColor: '#1a1a2e', color: '#fff' }}>
          <option value="">All Contacts</option>
          <option value="police">Police</option>
          <option value="fire">Fire</option>
          <option value="ambulance">Ambulance</option>
          <option value="hospital">Hospital</option>
          <option value="disaster_response">Disaster Response</option>
          <option value="ngo">NGO</option>
          <option value="government">Government</option>
          <option value="military">Military</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 12 }}>
        {contacts.map(c => (
          <div key={c.id} style={{ border: '1px solid #333', borderRadius: 8, padding: 12, borderLeft: `4px solid ${typeColors[c.type] || '#888'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4 style={{ margin: 0 }}>{c.name}</h4>
              <span style={{ fontSize: '0.75em', padding: '2px 8px', borderRadius: 12, backgroundColor: typeColors[c.type] || '#888', color: '#fff', textTransform: 'capitalize' }}>{c.type}</span>
            </div>
            <div style={{ marginTop: 8 }}><strong>Phone:</strong> {c.phone}</div>
            {c.alternate_phone && <div><strong>Alt:</strong> {c.alternate_phone}</div>}
            {c.email && <div><strong>Email:</strong> {c.email}</div>}
            <div style={{ fontSize: '0.85em', color: '#888' }}>{c.service_area} | Status: {c.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmergencyContacts;
