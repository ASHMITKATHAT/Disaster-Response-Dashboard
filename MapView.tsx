import React from 'react';
import MapComponent from '../components/MapComponent';
import VillageSelector from '../components/VillageSelector';
import SearchBar from '../components/SearchBar';
import InundationGauge from '../components/InundationGauge';

const MapView: React.FC = () => {
  return (
    <div className="map-view">
      <h1>Flood Risk Map</h1>
      
      <div className="map-controls">
        <SearchBar />
        <VillageSelector />
      </div>

      <div className="map-container">
        <MapComponent />
        <div className="map-sidebar">
          <InundationGauge riskLevel={65} />
          <div className="map-info">
            <h3>Active Warnings</h3>
            <ul>
              <li>Medium flood risk in District A</li>
              <li>Heavy rainfall expected in 3 hours</li>
              <li>River level above normal</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapView;