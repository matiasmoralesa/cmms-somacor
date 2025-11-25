/**
 * Inventory Service
 * API calls for spare parts management
 */
import api from './api';
import type { SparePart, StockMovement } from '../types/inventory.types';

const inventoryService = {
  /**
   * Get all spare parts
   */
  getSpareParts: async (params?: any): Promise<SparePart[]> => {
    const response = await api.get('/inventory/spare-parts/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  },

  /**
   * Get single spare part by ID
   */
  getSparePart: async (id: string): Promise<SparePart> => {
    const response = await api.get(`/inventory/spare-parts/${id}/`);
    return response.data;
  },

  /**
   * Create new spare part
   */
  createSparePart: async (data: Partial<SparePart>): Promise<SparePart> => {
    const response = await api.post('/inventory/spare-parts/', data);
    return response.data;
  },

  /**
   * Update existing spare part
   */
  updateSparePart: async (id: string, data: Partial<SparePart>): Promise<SparePart> => {
    const response = await api.put(`/inventory/spare-parts/${id}/`, data);
    return response.data;
  },

  /**
   * Delete spare part
   */
  deleteSparePart: async (id: string): Promise<void> => {
    await api.delete(`/inventory/spare-parts/${id}/`);
  },

  /**
   * Adjust stock
   */
  adjustStock: async (id: string, quantity: number, movementType: string, notes?: string): Promise<any> => {
    const response = await api.post(`/inventory/spare-parts/${id}/adjust-stock/`, {
      quantity,
      movement_type: movementType,
      notes,
    });
    return response.data;
  },

  /**
   * Get low stock items
   */
  getLowStock: async (): Promise<SparePart[]> => {
    const response = await api.get('/inventory/spare-parts/low-stock/');
    // Handle paginated response
    return response.data.results || response.data;
  },

  /**
   * Get stock movements
   */
  getStockMovements: async (sparePartId?: string): Promise<StockMovement[]> => {
    const params = sparePartId ? { spare_part: sparePartId } : {};
    const response = await api.get('/inventory/stock-movements/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  },
};

export default inventoryService;
