/**
 * Maintenance Service
 * API calls for maintenance plan management
 */
import api from './api';
import type { MaintenancePlan } from '../types/maintenance.types';

const maintenanceService = {
  /**
   * Get all maintenance plans
   */
  getMaintenancePlans: async (params?: any): Promise<MaintenancePlan[]> => {
    const response = await api.get('/maintenance/plans/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  },

  /**
   * Get single maintenance plan by ID
   */
  getMaintenancePlan: async (id: string): Promise<MaintenancePlan> => {
    const response = await api.get(`/maintenance/plans/${id}/`);
    return response.data;
  },

  /**
   * Create new maintenance plan
   */
  createMaintenancePlan: async (data: Partial<MaintenancePlan>): Promise<MaintenancePlan> => {
    const response = await api.post('/maintenance/plans/', data);
    return response.data;
  },

  /**
   * Update existing maintenance plan
   */
  updateMaintenancePlan: async (id: string, data: Partial<MaintenancePlan>): Promise<MaintenancePlan> => {
    const response = await api.put(`/maintenance/plans/${id}/`, data);
    return response.data;
  },

  /**
   * Delete maintenance plan
   */
  deleteMaintenancePlan: async (id: string): Promise<void> => {
    await api.delete(`/maintenance/plans/${id}/`);
  },

  /**
   * Pause maintenance plan
   */
  pauseMaintenancePlan: async (id: string): Promise<MaintenancePlan> => {
    const response = await api.patch(`/maintenance/plans/${id}/pause/`);
    return response.data;
  },

  /**
   * Resume maintenance plan
   */
  resumeMaintenancePlan: async (id: string): Promise<MaintenancePlan> => {
    const response = await api.patch(`/maintenance/plans/${id}/resume/`);
    return response.data;
  },
};

export default maintenanceService;
