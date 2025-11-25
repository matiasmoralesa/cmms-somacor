/**
 * Checklist Service
 */
import api from './api';
import {
  ChecklistTemplate,
  ChecklistResponse,
  ChecklistResponseCreate,
  ChecklistStatistics,
} from '../types/checklist.types';

const BASE_URL = '/checklists';

export const checklistService = {
  // Templates
  async getTemplates(params?: {
    vehicle_type?: string;
    is_system_template?: boolean;
    search?: string;
  }): Promise<{ count: number; results: ChecklistTemplate[] }> {
    const response = await api.get(`${BASE_URL}/templates/`, { params });
    return response.data;
  },

  async getTemplate(id: string): Promise<ChecklistTemplate> {
    const response = await api.get(`${BASE_URL}/templates/${id}/`);
    return response.data;
  },

  async getTemplatesByVehicleType(
    vehicleType: string
  ): Promise<ChecklistTemplate[]> {
    const response = await api.get(
      `${BASE_URL}/templates/by_vehicle_type/`,
      {
        params: { vehicle_type: vehicleType },
      }
    );
    return response.data;
  },

  // Responses
  async getResponses(params?: {
    template?: string;
    asset?: string;
    work_order?: string;
    passed?: boolean;
    completed_by?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ count: number; results: ChecklistResponse[] }> {
    const response = await api.get(`${BASE_URL}/responses/`, { params });
    return response.data;
  },

  async getResponse(id: string): Promise<ChecklistResponse> {
    const response = await api.get(`${BASE_URL}/responses/${id}/`);
    return response.data;
  },


  async createResponse(
    data: ChecklistResponseCreate
  ): Promise<ChecklistResponse> {
    const response = await api.post(`${BASE_URL}/responses/`, data);
    return response.data;
  },

  async completeChecklist(
    data: ChecklistResponseCreate
  ): Promise<ChecklistResponse> {
    const response = await api.post(`${BASE_URL}/responses/complete/`, data);
    return response.data;
  },

  async getResponsePdf(id: string): Promise<{ pdf_url: string }> {
    const response = await api.get(`${BASE_URL}/responses/${id}/pdf/`);
    return response.data;
  },

  async getResponsesByAsset(
    assetId: string,
    params?: { page?: number }
  ): Promise<{ count: number; results: ChecklistResponse[] }> {
    const response = await api.get(`${BASE_URL}/responses/by_asset/`, {
      params: { asset_id: assetId, ...params },
    });
    return response.data;
  },

  async getStatistics(params?: {
    template?: string;
    asset?: string;
  }): Promise<ChecklistStatistics> {
    const response = await api.get(`${BASE_URL}/responses/statistics/`, {
      params,
    });
    return response.data;
  },

  // Utility functions
  downloadPdf(pdfUrl: string): void {
    window.open(pdfUrl, '_blank');
  },
};

export default checklistService;
