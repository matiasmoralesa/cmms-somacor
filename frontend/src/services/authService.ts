/**
 * Authentication service - Firebase Authentication
 */
import { 
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';
import { auth } from '../config/firebase';
import api from './api';
import type {
  LoginCredentials,
  LoginResponse,
  User,
  PasswordChangeData,
  PasswordResetRequest,
  PasswordResetConfirm,
} from '../types/auth.types';

class AuthService {
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(
        auth,
        credentials.email,
        credentials.password
      );
      
      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();
      
      // Store Firebase token
      localStorage.setItem('firebaseToken', idToken);
      
      // Get user profile from backend (includes Django user data)
      const profile = await this.getProfile();
      
      // Store user data
      localStorage.setItem('user', JSON.stringify(profile));
      
      // Map User to LoginResponse.user format
      return {
        access: idToken,
        refresh: '', // Firebase handles refresh automatically
        user: {
          id: profile.id,
          email: profile.email,
          full_name: profile.full_name,
          role: profile.role,
          role_display: profile.role_display,
          is_admin: profile.role === 'ADMIN',
          is_supervisor: profile.role === 'SUPERVISOR',
          is_operador: profile.role === 'OPERADOR',
          employee_status: profile.employee_status,
          license_status: profile.license_status,
          permissions: [], // Will be populated from backend if needed
        },
      };
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(error.message || 'Login failed');
    }
  }

  async logout(): Promise<void> {
    try {
      // Sign out from Firebase
      await signOut(auth);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage
      localStorage.removeItem('firebaseToken');
      localStorage.removeItem('user');
    }
  }

  async getProfile(): Promise<User> {
    const response = await api.get<User>('/auth/profile/');
    return response.data;
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/auth/profile/', data);
    return response.data;
  }

  async changePassword(data: PasswordChangeData): Promise<void> {
    await api.post('/auth/password-change/', data);
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    await api.post('/auth/password-reset/', data);
  }

  async confirmPasswordReset(data: PasswordResetConfirm): Promise<void> {
    await api.post('/auth/password-reset-confirm/', data);
  }

  async checkLicenseStatus() {
    const response = await api.get('/auth/check-license/');
    return response.data;
  }

  async getIdToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (user) {
      try {
        return await user.getIdToken();
      } catch (error) {
        console.error('Error getting ID token:', error);
        return null;
      }
    }
    return null;
  }

  onAuthStateChanged(callback: (user: FirebaseUser | null) => void) {
    return onAuthStateChanged(auth, callback);
  }

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  getAccessToken(): string | null {
    return localStorage.getItem('firebaseToken');
  }

  getRefreshToken(): string | null {
    // Firebase handles refresh automatically
    return null;
  }

  isAuthenticated(): boolean {
    return !!auth.currentUser || !!this.getAccessToken();
  }

  getCurrentUser(): FirebaseUser | null {
    return auth.currentUser;
  }
}

export default new AuthService();
