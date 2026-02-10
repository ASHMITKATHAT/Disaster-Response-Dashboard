import { useState, useCallback } from 'react';

interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export const useMap = (initialLat = 26.9124, initialLng = 75.7873, initialZoom = 10) => {
  const [center, setCenter] = useState({ lat: initialLat, lng: initialLng });
  const [zoom, setZoom] = useState(initialZoom);
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [selectedArea, setSelectedArea] = useState<string | null>(null);

  const panTo = useCallback((lat: number, lng: number) => {
    setCenter({ lat, lng });
  }, []);

  const zoomTo = useCallback((level: number) => {
    setZoom(level);
  }, []);

  const fitBounds = useCallback((north: number, south: number, east: number, west: number) => {
    setBounds({ north, south, east, west });
  }, []);

  return {
    center,
    zoom,
    bounds,
    selectedArea,
    setCenter,
    setZoom,
    setBounds,
    setSelectedArea,
    panTo,
    zoomTo,
    fitBounds,
  };
};