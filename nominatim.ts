const NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search';

interface SearchResult {
  display_name: string;
  lat: string;
  lon: string;
  type: string;
}

export const nominatim = {
  async search(query: string): Promise<SearchResult[]> {
    try {
      const response = await fetch(
        `${NOMINATIM_URL}?q=${encodeURIComponent(query)}&format=json&limit=5`
      );
      
      if (!response.ok) {
        throw new Error('Search failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Nominatim search error:', error);
      return [];
    }
  },

  async reverseGeocode(lat: number, lng: number): Promise<string> {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`
      );
      
      if (!response.ok) {
        throw new Error('Reverse geocode failed');
      }
      
      const data = await response.json();
      return data.display_name || 'Unknown location';
    } catch (error) {
      console.error('Reverse geocode error:', error);
      return 'Unknown location';
    }
  },
};