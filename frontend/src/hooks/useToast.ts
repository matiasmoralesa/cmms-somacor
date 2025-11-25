/**
 * Hook for Toast Notifications
 */
import { useState, useCallback } from 'react';

interface ToastState {
  open: boolean;
  title: string;
  description?: string;
  type: 'success' | 'error' | 'warning' | 'info';
}

export const useToast = () => {
  const [toast, setToast] = useState<ToastState>({
    open: false,
    title: '',
    description: '',
    type: 'info',
  });

  const showToast = useCallback(
    (
      title: string,
      description?: string,
      type: 'success' | 'error' | 'warning' | 'info' = 'info'
    ) => {
      setToast({ open: true, title, description, type });
    },
    []
  );

  const success = useCallback((title: string, description?: string) => {
    showToast(title, description, 'success');
  }, [showToast]);

  const error = useCallback((title: string, description?: string) => {
    showToast(title, description, 'error');
  }, [showToast]);

  const warning = useCallback((title: string, description?: string) => {
    showToast(title, description, 'warning');
  }, [showToast]);

  const info = useCallback((title: string, description?: string) => {
    showToast(title, description, 'info');
  }, [showToast]);

  const closeToast = useCallback(() => {
    setToast((prev) => ({ ...prev, open: false }));
  }, []);

  return {
    toast,
    showToast,
    success,
    error,
    warning,
    info,
    closeToast,
  };
};
