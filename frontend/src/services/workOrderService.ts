/**
 * Work Order service
 */
import api from './api';
import type {
  WorkOrder,
  WorkOrderFormData,
  WorkOrderCompleteData,
  WorkOrderStatusChange,
} from '../types/workOrder.types';

class WorkOrderService {
  async getWorkOrders(params?: any) {
    const response = await api.get<any>('/work-orders/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  }

  async getWorkOrder(id: string) {
    const response = await api.get<WorkOrder>(`/work-orders/${id}/`);
    return response.data;
  }

  async createWorkOrder(data: WorkOrderFormData) {
    const response = await api.post<WorkOrder>('/work-orders/', data);
    return response.data;
  }

  async updateWorkOrder(id: string, data: Partial<WorkOrderFormData>) {
    const response = await api.put<WorkOrder>(`/work-orders/${id}/`, data);
    return response.data;
  }

  async deleteWorkOrder(id: string) {
    await api.delete(`/work-orders/${id}/`);
  }

  async completeWorkOrder(id: string, data: WorkOrderCompleteData) {
    const response = await api.post<WorkOrder>(`/work-orders/${id}/complete/`, data);
    return response.data;
  }

  async changeStatus(id: string, data: WorkOrderStatusChange) {
    const response = await api.patch<WorkOrder>(`/work-orders/${id}/change_status/`, data);
    return response.data;
  }

  async getMyAssignments(params?: any) {
    const response = await api.get<any>('/work-orders/my_assignments/', { params });
    // Handle paginated response
    return response.data.results || response.data;
  }

  async getStatistics() {
    const response = await api.get('/work-orders/statistics/');
    return response.data;
  }
}

export default new WorkOrderService();
