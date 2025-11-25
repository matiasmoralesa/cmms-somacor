/**
 * Authentication types
 */

export interface User {
  id: string;
  email: string;
  full_name: string;
  first_name: string;
  last_name: string;
  rut: string;
  phone?: string;
  role: 'ADMIN' | 'SUPERVISOR' | 'OPERADOR';
  role_display: string;
  employee_status: 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE';
  license_type?: 'MUNICIPAL' | 'INTERNAL' | 'OTHER';
  license_expiration_date?: string;
  license_status?: LicenseStatus;
  is_active: boolean;
  created_at: string;
}

export interface LicenseStatus {
  valid: boolean;
  expires_soon: boolean;
  days_until_expiration: number | null;
  expiration_date: string | null;
  type?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    role_display: string;
    is_admin: boolean;
    is_supervisor: boolean;
    is_operador: boolean;
    employee_status: string;
    license_status?: LicenseStatus;
    permissions: string[];
  };
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  permissions: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  uid: string;
  token: string;
  new_password: string;
  new_password_confirm: string;
}
