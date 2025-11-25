/**
 * Notification Service
 */
import api from './api';
import { Notification, NotificationPreference, NotificationStats } from '../types/notification.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const notificationService = {
  // Notifications
  getNotifications: async (params?: {
    notification_type?: string;
    priority?: string;
    is_read?: boolean;
    ordering?: string;
  }): Promise<PaginatedResponse<Notification>> => {
    const response = await api.get('/notifications/', { params });
    return response.data;
  },

  getNotification: async (id: string): Promise<Notification> => {
    const response = await api.get(`/notifications/${id}/`);
    return response.data;
  },

  getUnreadNotifications: async (): Promise<Notification[]> => {
    const response = await api.get('/notifications/unread/');
    return response.data;
  },

  getUnreadCount: async (): Promise<NotificationStats> => {
    const response = await api.get('/notifications/unread_count/');
    return response.data;
  },

  markAsRead: async (id: string): Promise<Notification> => {
    const response = await api.post(`/notifications/${id}/mark_read/`);
    return response.data;
  },

  markAllAsRead: async (): Promise<{ marked_read: number }> => {
    const response = await api.post('/notifications/mark_all_read/');
    return response.data;
  },

  clearRead: async (): Promise<{ deleted: number }> => {
    const response = await api.delete('/notifications/clear_read/');
    return response.data;
  },

  // Preferences
  getPreferences: async (): Promise<NotificationPreference[]> => {
    const response = await api.get('/notifications/preferences/');
    return response.data.results || response.data;
  },

  getDefaultPreferences: async (): Promise<NotificationPreference[]> => {
    const response = await api.get('/notifications/preferences/defaults/');
    return response.data;
  },

  updatePreference: async (
    id: string,
    data: Partial<NotificationPreference>
  ): Promise<NotificationPreference> => {
    const response = await api.patch(`/notifications/preferences/${id}/`, data);
    return response.data;
  },

  updateBulkPreferences: async (
    preferences: Partial<NotificationPreference>[]
  ): Promise<NotificationPreference[]> => {
    const response = await api.post('/notifications/preferences/update_bulk/', {
      preferences,
    });
    return response.data;
  },
};

export default notificationService;
