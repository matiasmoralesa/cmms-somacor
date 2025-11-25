/**
 * Report Service
 */
import api from './api';

const reportService = {
  // KPIs
  getKPIs: async (params?: {
    start_date?: string;
    end_date?: string;
    asset_id?: string;
  }) => {
    const response = await api.get('/reports/kpis/', { params });
    return response.data;
  },

  // Work Orders Summary
  getWorkOrdersSummary: async (params?: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/reports/work_orders_summary/', { params });
    return response.data;
  },

  // Asset Downtime
  getAssetDowntime: async (params?: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/reports/asset_downtime/', { params });
    return response.data;
  },

  // Spare Part Consumption
  getSparePartConsumption: async (params?: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/reports/spare_part_consumption/', { params });
    return response.data;
  },

  // Dashboard Summary
  getDashboardSummary: async (params?: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/reports/dashboard_summary/', { params });
    return response.data;
  },

  // Export CSV
  exportCSV: async (reportType: string, params?: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/reports/export_csv/', {
      params: { ...params, report_type: reportType },
      responseType: 'blob',
    });
    return response.data;
  },
};

export default reportService;
