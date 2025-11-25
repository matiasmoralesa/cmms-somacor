import api from './api';
import {
  MachineStatus,
  MachineStatusFormData,
  StatusHistory,
  ChartData,
  StatusDistribution,
} from '../types/machineStatus.types';

const STATUS_URL = '/machine-status';

export const machineStatusService = {
  // Get all status updates
  getAll: async (params?: {
    asset?: string;
    status_type?: string;
    reported_by?: string;
  }): Promise<MachineStatus[]> => {
    const response = await api.get(STATUS_URL, { params });
    return response.data.results || response.data;
  },

  // Get status by ID
  getById: async (id: string): Promise<MachineStatus> => {
    const response = await api.get(`${STATUS_URL}/${id}/`);
    return response.data;
  },

  // Create new status update
  create: async (data: MachineStatusFormData): Promise<MachineStatus> => {
    const response = await api.post(STATUS_URL + '/', data);
    return response.data;
  },

  // Get my assigned assets (OPERADOR)
  getMyAssets: async () => {
    const response = await api.get(`${STATUS_URL}/my_assets/`);
    return response.data;
  },

  // Get status history for asset
  getAssetHistory: async (assetId: string): Promise<{ asset: any; history: StatusHistory[]; count: number }> => {
    const response = await api.get(`${STATUS_URL}/asset/${assetId}/history/`);
    return response.data;
  },

  // Get current status for asset
  getCurrentStatus: async (assetId: string) => {
    const response = await api.get(`${STATUS_URL}/asset/${assetId}/current/`);
    return response.data;
  },

  // Get chart data for asset
  getChartData: async (
    assetId: string,
    days: number = 30
  ): Promise<{
    asset: any;
    chart_data: ChartData;
    status_distribution: StatusDistribution[];
    date_range: any;
  }> => {
    const response = await api.get(`${STATUS_URL}/asset/${assetId}/chart-data/`, {
      params: { days },
    });
    return response.data;
  },

  // Generate maintenance report PDF
  downloadMaintenanceReport: async (assetId: string): Promise<Blob> => {
    const response = await api.get(`${STATUS_URL}/asset/${assetId}/maintenance-report/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default machineStatusService;
