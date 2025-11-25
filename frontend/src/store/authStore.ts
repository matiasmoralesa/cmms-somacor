/**
 * Authentication store using Zustand
 */
import { create } from 'zustand';
import authService from '../services/authService';
import type { AuthState, LoginCredentials, User } from '../types/auth.types';

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => void;
  updateUser: (user: User) => void;
  clearError: () => void;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (...permissions: string[]) => boolean;
  hasAllPermissions: (...permissions: string[]) => boolean;
  isAdmin: () => boolean;
  isSupervisor: () => boolean;
  isOperador: () => boolean;
  canViewAllResources: () => boolean;
}

const useAuthStore = create<AuthState & AuthActions>((set, get) => ({
  // State
  user: null,
  accessToken: null,
  refreshToken: null,
  permissions: [],
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Actions
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login(credentials);
      
      set({
        user: response.user as unknown as User,
        accessToken: response.access,
        refreshToken: response.refresh,
        permissions: response.user.permissions,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.error ||
                          'Error al iniciar sesión';
      set({
        isLoading: false,
        error: errorMessage,
        isAuthenticated: false,
      });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        permissions: [],
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
    }
  },

  loadUser: () => {
    const user = authService.getStoredUser();
    const accessToken = authService.getAccessToken();
    const refreshToken = authService.getRefreshToken();

    if (user && accessToken) {
      set({
        user,
        accessToken,
        refreshToken,
        permissions: (user as any).permissions || [],
        isAuthenticated: true,
      });
    }
  },

  updateUser: (user) => {
    set({ user });
    localStorage.setItem('user', JSON.stringify(user));
  },

  clearError: () => {
    set({ error: null });
  },

  // Permission helpers
  hasPermission: (permission) => {
    const { permissions } = get();
    return permissions.includes(permission);
  },

  hasAnyPermission: (...permissions) => {
    const { permissions: userPermissions } = get();
    return permissions.some(p => userPermissions.includes(p));
  },

  hasAllPermissions: (...permissions) => {
    const { permissions: userPermissions } = get();
    return permissions.every(p => userPermissions.includes(p));
  },

  isAdmin: () => {
    const { user } = get();
    return user?.role === 'ADMIN';
  },

  isSupervisor: () => {
    const { user } = get();
    return user?.role === 'SUPERVISOR';
  },

  isOperador: () => {
    const { user } = get();
    return user?.role === 'OPERADOR';
  },

  canViewAllResources: () => {
    const { user } = get();
    return user?.role === 'ADMIN' || user?.role === 'SUPERVISOR';
  },
}));

export default useAuthStore;
