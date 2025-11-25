import api from './api';
import { User, UserListItem, UserFormData, Role, PasswordResetData } from '../types/user.types';

const USERS_URL = '/auth/users-management';
const ROLES_URL = '/auth/roles';

export const userService = {
  // Get all users
  getAll: async (params?: {
    search?: string;
    role?: string;
    employee_status?: string;
    is_active?: boolean;
  }): Promise<UserListItem[]> => {
    const response = await api.get(USERS_URL, { params });
    return response.data.results || response.data;
  },

  // Get user by ID
  getById: async (id: string): Promise<User> => {
    const response = await api.get(`${USERS_URL}/${id}/`);
    return response.data;
  },

  // Create new user
  create: async (data: UserFormData): Promise<{ user: User; temporary_password: string; email_sent: boolean }> => {
    const response = await api.post(USERS_URL + '/', data);
    return response.data;
  },

  // Update user
  update: async (id: string, data: Partial<UserFormData>): Promise<User> => {
    const response = await api.put(`${USERS_URL}/${id}/`, data);
    return response.data;
  },

  // Delete user (soft delete)
  delete: async (id: string): Promise<void> => {
    await api.delete(`${USERS_URL}/${id}/`);
  },

  // Activate user
  activate: async (id: string): Promise<{ message: string; user: User }> => {
    const response = await api.patch(`${USERS_URL}/${id}/activate/`);
    return response.data;
  },

  // Deactivate user
  deactivate: async (id: string): Promise<{ message: string; user: User }> => {
    const response = await api.patch(`${USERS_URL}/${id}/deactivate/`);
    return response.data;
  },

  // Reset user password
  resetPassword: async (id: string, data: PasswordResetData): Promise<{ message: string; email_sent: boolean }> => {
    const response = await api.post(`${USERS_URL}/${id}/reset_password/`, data);
    return response.data;
  },

  // Get all roles
  getRoles: async (): Promise<Role[]> => {
    const response = await api.get(ROLES_URL);
    return response.data.results || response.data;
  },
};

export default userService;
