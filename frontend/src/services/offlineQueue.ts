/**
 * Offline Queue Service
 * Handles queuing of notifications when offline and syncing when back online
 */

interface QueuedNotification {
  id: string;
  timestamp: number;
  data: any;
}

const QUEUE_KEY = 'cmms_notification_queue';
const MAX_QUEUE_SIZE = 100;

class OfflineQueueService {
  private queue: QueuedNotification[] = [];
  private isOnline: boolean = navigator.onLine;
  private syncCallbacks: Array<(notifications: QueuedNotification[]) => Promise<void>> = [];

  constructor() {
    this.loadQueue();
    this.setupOnlineListener();
  }

  /**
   * Load queue from localStorage
   */
  private loadQueue() {
    try {
      const stored = localStorage.getItem(QUEUE_KEY);
      if (stored) {
        this.queue = JSON.parse(stored);
      }
    } catch (error) {
      console.error('Error loading offline queue:', error);
      this.queue = [];
    }
  }

  /**
   * Save queue to localStorage
   */
  private saveQueue() {
    try {
      localStorage.setItem(QUEUE_KEY, JSON.stringify(this.queue));
    } catch (error) {
      console.error('Error saving offline queue:', error);
    }
  }

  /**
   * Setup online/offline event listeners
   */
  private setupOnlineListener() {
    window.addEventListener('online', () => {
      console.log('Connection restored. Syncing offline queue...');
      this.isOnline = true;
      this.syncQueue();
    });

    window.addEventListener('offline', () => {
      console.log('Connection lost. Queuing notifications...');
      this.isOnline = false;
    });
  }

  /**
   * Add notification to queue
   */
  enqueue(notification: any): void {
    const queuedNotification: QueuedNotification = {
      id: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      data: notification,
    };

    this.queue.push(queuedNotification);

    // Limit queue size
    if (this.queue.length > MAX_QUEUE_SIZE) {
      this.queue = this.queue.slice(-MAX_QUEUE_SIZE);
    }

    this.saveQueue();
  }

  /**
   * Get all queued notifications
   */
  getQueue(): QueuedNotification[] {
    return [...this.queue];
  }

  /**
   * Clear queue
   */
  clearQueue(): void {
    this.queue = [];
    this.saveQueue();
  }

  /**
   * Register sync callback
   */
  onSync(callback: (notifications: QueuedNotification[]) => Promise<void>): void {
    this.syncCallbacks.push(callback);
  }

  /**
   * Sync queue when back online
   */
  async syncQueue(): Promise<void> {
    if (!this.isOnline || this.queue.length === 0) {
      return;
    }

    const notificationsToSync = [...this.queue];

    try {
      // Call all registered sync callbacks
      for (const callback of this.syncCallbacks) {
        await callback(notificationsToSync);
      }

      // Clear queue after successful sync
      this.clearQueue();
      console.log(`Synced ${notificationsToSync.length} offline notifications`);
    } catch (error) {
      console.error('Error syncing offline queue:', error);
    }
  }

  /**
   * Check if online
   */
  isConnectionOnline(): boolean {
    return this.isOnline;
  }

  /**
   * Get queue size
   */
  getQueueSize(): number {
    return this.queue.length;
  }
}

// Singleton instance
const offlineQueueService = new OfflineQueueService();

export default offlineQueueService;
