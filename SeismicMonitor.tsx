import React, { useState, useEffect } from 'react';

interface SeismicEvent {
  event_id: string;
  timestamp: string;
  magnitude: { local_magnitude_ml: number; classification: string };
  intensity: { mmi: number; damage_level: string; alert_level: string };
  epicenter: { epicenter: { lat: number; lon: number }; depth_km: number };
}

const SeismicMonitor: React.FC = () => {
  const [events, setEvents] = useState<SeismicEvent[]>([]);
  const [waveform, setWaveform] = useState<number[]>([]);
  const [status, setStatus] = useState<string>('idle');

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('/api/seismic/events?hours=48');
        const data = await res.json();
        if (data.success) setEvents(data.events);
      } catch (e) {
        console.error('Failed to fetch seismic events');
      }
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchWaveform = async () => {
      try {
        const res = await fetch('/api/seismic/monitor/data?station=STN001');
        const data = await res.json();
        if (data.success) {
          setWaveform(data.data.waveform);
          setStatus(data.data.alert_level);
        }
      } catch (e) { /* ignore */ }
    };
    fetchWaveform();
    const interval = setInterval(fetchWaveform, 5000);
    return () => clearInterval(interval);
  }, []);

  const alertColors: Record<string, string> = { green: '#4CAF50', yellow: '#FFC107', orange: '#FF9800', red: '#F44336', unknown: '#9E9E9E' };

  return (
    <div className="seismic-monitor">
      <h2>Seismic Monitoring</h2>
      <div className="status-bar" style={{ backgroundColor: alertColors[status] || '#9E9E9E', padding: '8px 16px', borderRadius: 4, color: '#fff', marginBottom: 16 }}>
        Alert Level: {status.toUpperCase()}
      </div>
      <div className="waveform-container" style={{ height: 120, backgroundColor: '#1a1a2e', borderRadius: 8, padding: 8, marginBottom: 16, overflow: 'hidden' }}>
        {waveform.length > 0 && (
          <svg width="100%" height="100%" viewBox={`0 0 ${waveform.length} 100`} preserveAspectRatio="none">
            <polyline fill="none" stroke="#00E5FF" strokeWidth="2" points={waveform.map((v, i) => `${i},${50 - v * 20}`).join(' ')} />
          </svg>
        )}
      </div>
      <div className="events-list">
        <h3>Recent Seismic Events</h3>
        {events.length === 0 && <p>No recent events detected</p>}
        {events.map(evt => (
          <div key={evt.event_id} className="event-card" style={{ border: '1px solid #333', borderRadius: 8, padding: 12, marginBottom: 8 }}>
            <div><strong>{evt.event_id}</strong> - M{evt.magnitude?.local_magnitude_ml?.toFixed(1)} ({evt.magnitude?.classification})</div>
            <div style={{ fontSize: '0.85em', color: '#888' }}>{evt.timestamp} | Depth: {evt.epicenter?.depth_km?.toFixed(1)}km | MMI: {evt.intensity?.mmi?.toFixed(1)}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SeismicMonitor;
