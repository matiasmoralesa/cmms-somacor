/**
 * Toast Container Component
 */
import React, { useState, useEffect } from 'react';
import ToastNotification from './ToastNotification';
import { Notification } from '../../types/notification.types';
import useNotificationStore from '../../store/notificationStore';

const ToastContainer: React.FC = () => {
  const [toasts, setToasts] = useState<Notification[]>([]);
  const { notifications } = useNotificationStore();

  useEffect(() => {
    // Show toast for new unread notifications
    const newNotifications = notifications.filter(
      (n) => !n.is_read && !toasts.find((t) => t.id === n.id)
    );

    if (newNotifications.length > 0) {
      setToasts((prev) => [...newNotifications.slice(0, 3), ...prev].slice(0, 3));
    }
  }, [notifications]);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-4 pointer-events-none">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastNotification
            notification={toast}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
    </div>
  );
};

export default ToastContainer;
