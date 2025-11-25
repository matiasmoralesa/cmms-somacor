/**
 * Toast Notification Component
 */
import React, { useEffect } from 'react';
import { Notification } from '../../types/notification.types';

interface ToastNotificationProps {
  notification: Notification;
  onClose: () => void;
  duration?: number;
}

const ToastNotification: React.FC<ToastNotificationProps> = ({
  notification,
  onClose,
  duration = 5000,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getPriorityStyles = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-50 border-red-500 text-red-900';
      case 'HIGH':
        return 'bg-orange-50 border-orange-500 text-orange-900';
      case 'MEDIUM':
        return 'bg-amber-50 border-amber-500 text-amber-900';
      default:
        return 'bg-blue-50 border-blue-500 text-blue-900';
    }
  };

  const getIcon = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return '🔴';
      case 'HIGH':
        return '🟠';
      case 'MEDIUM':
        return '🟡';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div
      className={`max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border-l-4 ${getPriorityStyles(
        notification.priority
      )}`}
    >
      <div className="p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0 text-2xl">
            {getIcon(notification.priority)}
          </div>
          <div className="ml-3 w-0 flex-1">
            <p className="text-sm font-medium">{notification.title}</p>
            <p className="mt-1 text-sm opacity-90">{notification.message}</p>
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              onClick={onClose}
              className="inline-flex text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ToastNotification;
