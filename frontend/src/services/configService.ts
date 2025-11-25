/**
 * Configuration Service
 * API calls for master data and system configuration
 */
import api from './api';

export interface AssetCategory {
  id: string;
  name: string;
  code: string;
  description: string;
  parent: string | null;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  name: string;
  code: string;
  description: string;
  address: string;
  city: string;
  state: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface Priority {
  id: string;
  name: string;
  code: string;
  description: string;
  level: number;
  color: string;
  response_time_hours: number | null;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkOrderType {
  id: string;
  name: string;
  code: string;
  description: string;
  requires_approval: boolean;
  default_priority: string | null;
  estimated_hours: number | null;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface SystemParameter {
  id: string;
  key: string;
  value: string;
  data_type: 'STRING' | 'INTEGER' | 'FLOAT' | 'BOOLEAN' | 'JSON';
  description: string;
  is_sensitive: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuditLog {
  id: string;
  model_name: string;
  object_id: string;
  object_repr: string;
  action: 'CREATE' | 'UPDATE' | 'DELETE';
  changes: Record<string, any>;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  } | null;
  timestamp: string;
  ip_address: string | null;
}

// Asset Categories
export const getAssetCategories = async (params?: any) => {
  const response = await api.get('/config/asset-categories/', { params });
  return response.data;
};

export const getAssetCategory = async (id: string) => {
  const response = await api.get(`/config/asset-categories/${id}/`);
  return response.data;
};

export const createAssetCategory = async (data: Partial<AssetCategory>) => {
  const response = await api.post('/config/asset-categories/', data);
  return response.data;
};

export const updateAssetCategory = async (id: string, data: Partial<AssetCategory>) => {
  const response = await api.put(`/config/asset-categories/${id}/`, data);
  return response.data;
};

export const deleteAssetCategory = async (id: string) => {
  await api.delete(`/config/asset-categories/${id}/`);
};

// Locations
export const getLocations = async (params?: any) => {
  const response = await api.get('/config/locations/', { params });
  return response.data;
};

export const getLocation = async (id: string) => {
  const response = await api.get(`/config/locations/${id}/`);
  return response.data;
};

export const createLocation = async (data: Partial<Location>) => {
  const response = await api.post('/config/locations/', data);
  return response.data;
};

export const updateLocation = async (id: string, data: Partial<Location>) => {
  const response = await api.put(`/config/locations/${id}/`, data);
  return response.data;
};

export const deleteLocation = async (id: string) => {
  await api.delete(`/config/locations/${id}/`);
};

// Priorities
export const getPriorities = async (params?: any) => {
  const response = await api.get('/config/priorities/', { params });
  return response.data;
};

export const getPriority = async (id: string) => {
  const response = await api.get(`/config/priorities/${id}/`);
  return response.data;
};

export const createPriority = async (data: Partial<Priority>) => {
  const response = await api.post('/config/priorities/', data);
  return response.data;
};

export const updatePriority = async (id: string, data: Partial<Priority>) => {
  const response = await api.put(`/config/priorities/${id}/`, data);
  return response.data;
};

export const deletePriority = async (id: string) => {
  await api.delete(`/config/priorities/${id}/`);
};

// Work Order Types
export const getWorkOrderTypes = async (params?: any) => {
  const response = await api.get('/config/work-order-types/', { params });
  return response.data;
};

export const getWorkOrderType = async (id: string) => {
  const response = await api.get(`/config/work-order-types/${id}/`);
  return response.data;
};

export const createWorkOrderType = async (data: Partial<WorkOrderType>) => {
  const response = await api.post('/config/work-order-types/', data);
  return response.data;
};

export const updateWorkOrderType = async (id: string, data: Partial<WorkOrderType>) => {
  const response = await api.put(`/config/work-order-types/${id}/`, data);
  return response.data;
};

export const deleteWorkOrderType = async (id: string) => {
  await api.delete(`/config/work-order-types/${id}/`);
};

// System Parameters
export const getSystemParameters = async (params?: any) => {
  const response = await api.get('/config/system-parameters/', { params });
  return response.data;
};

export const getSystemParameter = async (id: string) => {
  const response = await api.get(`/config/system-parameters/${id}/`);
  return response.data;
};

export const getSystemParameterByKey = async (key: string) => {
  const response = await api.get('/config/system-parameters/by_key/', { params: { key } });
  return response.data;
};

export const createSystemParameter = async (data: Partial<SystemParameter>) => {
  const response = await api.post('/config/system-parameters/', data);
  return response.data;
};

export const updateSystemParameter = async (id: string, data: Partial<SystemParameter>) => {
  const response = await api.put(`/config/system-parameters/${id}/`, data);
  return response.data;
};

export const deleteSystemParameter = async (id: string) => {
  await api.delete(`/config/system-parameters/${id}/`);
};

// Audit Logs
export const getAuditLogs = async (params?: any) => {
  const response = await api.get('/config/audit-logs/', { params });
  return response.data;
};

export const getAuditLogsForObject = async (modelName: string, objectId: string) => {
  const response = await api.get('/config/audit-logs/for_object/', {
    params: { model_name: modelName, object_id: objectId }
  });
  return response.data;
};
