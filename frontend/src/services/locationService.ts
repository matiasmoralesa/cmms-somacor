import api from './api';
import { Location, LocationListItem, LocationFormData } from '../types/location.types';

const LOCATIONS_URL = '/assets/locations';

export const locationService = {
  // Get all locations
  getAll: async (params?: { search?: string; is_active?: boolean }): Promise<LocationListItem[]> => {
    const response = await api.get(LOCATIONS_URL, { params });
    return response.data.results || response.data;
  },

  // Get location by ID
  getById: async (id: string): Promise<Location> => {
    const response = await api.get(`${LOCATIONS_URL}/${id}/`);
    return response.data;
  },

  // Create new location
  create: async (data: LocationFormData): Promise<Location> => {
    const response = await api.post(LOCATIONS_URL + '/', data);
    return response.data;
  },

  // Update location
  update: async (id: string, data: Partial<LocationFormData>): Promise<Location> => {
    const response = await api.put(`${LOCATIONS_URL}/${id}/`, data);
    return response.data;
  },

  // Delete location
  delete: async (id: string): Promise<void> => {
    await api.delete(`${LOCATIONS_URL}/${id}/`);
  },

  // Get assets in location
  getAssets: async (id: string) => {
    const response = await api.get(`${LOCATIONS_URL}/${id}/assets/`);
    return response.data;
  },
};

export default locationService;
