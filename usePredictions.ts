import { useState, useEffect } from 'react';
import { api } from '../services/api';

interface PredictionData {
  riskLevel: number;
  confidence: number;
  factors: string[];
  timestamp: string;
}

export const usePredictions = (lat?: number, lng?: number) => {
  const [predictions, setPredictions] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPredictions = async (latitude: number, longitude: number) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.getFloodPredictions(latitude, longitude);
      
      if (response.success && response.data) {
        setPredictions(response.data);
      } else {
        setError(response.error || 'Failed to fetch predictions');
        // Fallback to mock data
        setPredictions({
          riskLevel: Math.random() * 100,
          confidence: 85,
          factors: ['rainfall', 'soil_moisture', 'terrain'],
          timestamp: new Date().toISOString(),
        });
      }
    } catch (err) {
      setError('Network error');
      // Fallback to mock data
      setPredictions({
        riskLevel: Math.random() * 100,
        confidence: 75,
        factors: ['rainfall', 'soil_moisture'],
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (lat && lng) {
      fetchPredictions(lat, lng);
    }
  }, [lat, lng]);

  const refetch = () => {
    if (lat && lng) {
      fetchPredictions(lat, lng);
    }
  };

  return { predictions, loading, error, refetch };
};