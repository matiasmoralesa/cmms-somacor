export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  rut: string;
  phone?: string;
  role: string;
  role_name: string;
  employee_status: 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE';
  license_type?: 'MUNICIPAL' | 'INTERNAL' | 'OTHER';
  license_expiration_date?: string;
  license_photo_url?: string;
  license_status?: 'valid' | 'expiring_soon' | 'expired' | 'N/A';
  telegram_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListItem {
  id: string;
  email: string;
  full_name: string;
  role: string;
  role_name: string;
  employee_status: string;
  is_active: boolean;
  created_at: string;
}

export interface UserFormData {
  email: string;
  first_name: string;
  last_name: string;
  rut: string;
  phone?: string;
  role: string;
  employee_status: 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE';
  license_type?: 'MUNICIPAL' | 'INTERNAL' | 'OTHER';
  license_expiration_date?: string;
  license_photo_url?: string;
  telegram_id?: string;
  is_active: boolean;
}

export interface Role {
  id: string;
  name: string;
  display_name: string;
  description?: string;
}

export interface PasswordResetData {
  new_password: string;
  new_password_confirm: string;
  send_email: boolean;
}
