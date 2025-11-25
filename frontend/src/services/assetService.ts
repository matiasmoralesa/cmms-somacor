/**
 * Asset Service
 * API calls for asset management
 */
import api from './api';
import type { Asset } from '../types/asset.types';

const assetService = {
  /**
   * Get all assets
   */
  getAssets: async (params?: any): Promise<Asset[]> => {
    const response = await api.get('/assets/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  },

  /**
   * Get single asset by ID
   */
  getAsset: async (id: string): Promise<Asset> => {
    const response = await api.get(`/assets/${id}/`);
    return response.data;
  },

  /**
   * Create new asset
   */
  createAsset: async (data: Partial<Asset>): Promise<Asset> => {
    const response = await api.post('/assets/', data);
    return response.data;
  },

  /**
   * Update existing asset
   */
  updateAsset: async (id: string, data: Partial<Asset>): Promise<Asset> => {
    const response = await api.put(`/assets/${id}/`, data);
    return response.data;
  },

  /**
   * Delete asset
   */
  deleteAsset: async (id: string): Promise<void> => {
    await api.delete(`/assets/${id}/`);
  },

  /**
   * Upload document for asset
   */
  uploadDocument: async (id: string, file: File, documentType: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const response = await api.post(`/assets/${id}/upload-document/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Get documents for asset
   */
  getDocuments: async (id: string): Promise<any[]> => {
    const response = await api.get(`/assets/${id}/documents/`);
    return response.data;
  },
};

export default assetService;
export type { Asset };
