import { useState, useEffect } from 'react';

interface Location {
  lat: number;
  lng: number;
  accuracy?: number;
  error?: string;
}

export const useLocation = () => {
  const [location, setLocation] = useState<Location | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      setLoading(false);
      return;
    }

    const successHandler = (position: GeolocationPosition) => {
      setLocation({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        accuracy: position.coords.accuracy,
      });
      setLoading(false);
      setError(null);
    };

    const errorHandler = (error: GeolocationPositionError) => {
      setError(error.message);
      setLoading(false);
    };

    setLoading(true);
    navigator.geolocation.getCurrentPosition(successHandler, errorHandler);

    // Optional: Watch position for real-time updates
    const watchId = navigator.geolocation.watchPosition(successHandler, errorHandler);

    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, []);

  return { location, loading, error };
};