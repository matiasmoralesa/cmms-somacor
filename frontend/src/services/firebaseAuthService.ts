/**
 * Firebase Authentication Service
 * Replaces Django JWT authentication with Firebase Auth
 */
import {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser,
  updateProfile,
  updatePassword,
  sendPasswordResetEmail,
  EmailAuthProvider,
  reauthenticateWithCredential,
} from 'firebase/auth';
import { auth } from '../config/firebase';
import api from './api';
import type { User, LoginCredentials } from '../types/auth.types';

class FirebaseAuthService {
  private currentUser: User | null = null;

  /**
   * Initialize auth state listener
   */
  init(callback: (user: User | null) => void) {
    onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in
        const user = await this.syncUserWithBackend(firebaseUser);
        this.currentUser = user;
        callback(user);
      } else {
        // User is signed out
        this.currentUser = null;
        callback(null);
      }
    });
  }

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<User> {
    try {
      const userCredential = await signInWithEmailAndPassword(
        auth,
        credentials.email,
        credentials.password
      );

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();

      // Sync with backend and get user data
      const user = await this.syncUserWithBackend(userCredential.user, idToken);

      // Store user data
      localStorage.setItem('user', JSON.stringify(user));
      this.currentUser = user;

      return user;
    } catch (error: any) {
      console.error('Login error:', error);
      throw new Error(this.getErrorMessage(error.code));
    }
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    try {
      await signOut(auth);
      localStorage.removeItem('user');
      this.currentUser = null;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  /**
   * Get current Firebase user
   */
  getCurrentFirebaseUser(): FirebaseUser | null {
    return auth.currentUser;
  }

  /**
   * Get current user data
   */
  getCurrentUser(): User | null {
    return this.currentUser;
  }

  /**
   * Get Firebase ID token for API calls
   */
  async getIdToken(): Promise<string | null> {
    const user = auth.currentUser;
    if (user) {
      return await user.getIdToken();
    }
    return null;
  }

  /**
   * Sync Firebase user with backend
   */
  private async syncUserWithBackend(
    firebaseUser: FirebaseUser,
    idToken?: string
  ): Promise<User> {
    try {
      // Get or create user in backend
      const token = idToken || (await firebaseUser.getIdToken());

      // Call backend to sync user
      const response = await api.post<User>(
        '/auth/firebase-login/',
        {
          firebase_token: token,
          email: firebaseUser.email,
          display_name: firebaseUser.displayName,
          photo_url: firebaseUser.photoURL,
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error syncing user with backend:', error);

      // Fallback: create user object from Firebase data
      return {
        id: firebaseUser.uid,
        email: firebaseUser.email || '',
        full_name: firebaseUser.displayName || '',
        first_name: firebaseUser.displayName?.split(' ')[0] || '',
        last_name: firebaseUser.displayName?.split(' ').slice(1).join(' ') || '',
        rut: '',
        phone: firebaseUser.phoneNumber || undefined,
        role: 'OPERADOR', // Default role
        role_display: 'Operador',
        employee_status: 'ACTIVE',
        is_active: true,
        created_at: new Date().toISOString(),
      };
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(data: { displayName?: string; photoURL?: string }): Promise<void> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('No user logged in');
    }

    try {
      await updateProfile(user, data);

      // Sync with backend
      await this.syncUserWithBackend(user);
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  /**
   * Change password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const user = auth.currentUser;
    if (!user || !user.email) {
      throw new Error('No user logged in');
    }

    try {
      // Re-authenticate user
      const credential = EmailAuthProvider.credential(user.email, currentPassword);
      await reauthenticateWithCredential(user, credential);

      // Update password
      await updatePassword(user, newPassword);
    } catch (error: any) {
      console.error('Error changing password:', error);
      throw new Error(this.getErrorMessage(error.code));
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error: any) {
      console.error('Error requesting password reset:', error);
      throw new Error(this.getErrorMessage(error.code));
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return auth.currentUser !== null;
  }

  /**
   * Get stored user from localStorage
   */
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

  /**
   * Get user-friendly error message
   */
  private getErrorMessage(errorCode: string): string {
    const errorMessages: Record<string, string> = {
      'auth/invalid-email': 'Correo electrónico inválido',
      'auth/user-disabled': 'Usuario deshabilitado',
      'auth/user-not-found': 'Usuario no encontrado',
      'auth/wrong-password': 'Contraseña incorrecta',
      'auth/email-already-in-use': 'El correo ya está en uso',
      'auth/weak-password': 'La contraseña es muy débil',
      'auth/too-many-requests': 'Demasiados intentos. Intenta más tarde',
      'auth/network-request-failed': 'Error de red. Verifica tu conexión',
      'auth/requires-recent-login': 'Debes iniciar sesión nuevamente',
    };

    return errorMessages[errorCode] || 'Error de autenticación';
  }
}

export default new FirebaseAuthService();
