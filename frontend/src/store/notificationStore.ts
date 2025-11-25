/**
 * Notification Store using Zustand
 */
import { create } from 'zustand';
import { Notification } from '../types/notification.types';
import notificationService from '../services/notificationService';
import offlineQueueService from '../services/offlineQueue';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  isOnline: boolean;
  queueSize: number;
  
  // Actions
  fetchNotifications: () => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  clearRead: () => Promise<void>;
  addNotification: (notification: Notification) => void;
  startPolling: () => void;
  stopPolling: () => void;
  syncOfflineQueue: () => Promise<void>;
  updateOnlineStatus: (isOnline: boolean) => void;
}

let pollingInterval: NodeJS.Timeout | null = null;

const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,
  isOnline: navigator.onLine,
  queueSize: offlineQueueService.getQueueSize(),

  fetchNotifications: async () => {
    try {
      set({ loading: true, error: null });
      const response = await notificationService.getNotifications({
        ordering: '-created_at',
      });
      set({
        notifications: Array.isArray(response) ? response : response.results,
        loading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || 'Error al cargar notificaciones',
        loading: false,
      });
    }
  },

  fetchUnreadCount: async () => {
    try {
      const data = await notificationService.getUnreadCount();
      set({ unreadCount: data.count });
    } catch (error: any) {
      console.error('Error fetching unread count:', error);
    }
  },

  markAsRead: async (id: string) => {
    try {
      await notificationService.markAsRead(id);
      
      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n
        ),
        unreadCount: Math.max(0, state.unreadCount - 1),
      }));
    } catch (error: any) {
      console.error('Error marking notification as read:', error);
    }
  },

  markAllAsRead: async () => {
    try {
      await notificationService.markAllAsRead();
      
      // Update local state
      set((state) => ({
        notifications: state.notifications.map((n) => ({
          ...n,
          is_read: true,
          read_at: new Date().toISOString(),
        })),
        unreadCount: 0,
      }));
    } catch (error: any) {
      console.error('Error marking all as read:', error);
    }
  },

  clearRead: async () => {
    try {
      await notificationService.clearRead();
      
      // Update local state
      set((state) => ({
        notifications: state.notifications.filter((n) => !n.is_read),
      }));
    } catch (error: any) {
      console.error('Error clearing read notifications:', error);
    }
  },

  addNotification: (notification: Notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + 1,
    }));
  },

  startPolling: () => {
    const { fetchUnreadCount } = get();
    
    // Initial fetch
    fetchUnreadCount();
    
    // Poll every 30 seconds
    if (!pollingInterval) {
      pollingInterval = setInterval(() => {
        fetchUnreadCount();
      }, 30000);
    }
  },

  stopPolling: () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      pollingInterval = null;
    }
  },

  syncOfflineQueue: async () => {
    try {
      await offlineQueueService.syncQueue();
      set({ queueSize: 0 });
      
      // Refresh notifications after sync
      const { fetchNotifications, fetchUnreadCount } = get();
      await fetchNotifications();
      await fetchUnreadCount();
    } catch (error: any) {
      console.error('Error syncing offline queue:', error);
    }
  },

  updateOnlineStatus: (isOnline: boolean) => {
    set({ isOnline, queueSize: offlineQueueService.getQueueSize() });
    
    if (isOnline) {
      const { syncOfflineQueue } = get();
      syncOfflineQueue();
    }
  },
}));

// Setup offline queue sync callback
offlineQueueService.onSync(async (notifications) => {
  console.log(`Syncing ${notifications.length} offline notifications`);
  // Here you could process the queued notifications
  // For now, we just log them
});

// Setup online/offline listeners
window.addEventListener('online', () => {
  useNotificationStore.getState().updateOnlineStatus(true);
});

window.addEventListener('offline', () => {
  useNotificationStore.getState().updateOnlineStatus(false);
});

export default useNotificationStore;
