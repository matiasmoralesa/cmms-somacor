/**
 * Asset Type Definitions
 */

export interface Asset {
  id: string;
  name: string;
  asset_code: string;
  vehicle_type: string;
  vehicle_type_display?: string;
  serial_number: string;
  license_plate?: string;
  manufacturer?: string;
  model?: string;
  installation_date?: string;
  status: string;
  status_display?: string;
  location?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AssetDocument {
  id: string;
  asset: string;
  document_type: string;
  file_url: string;
  file_name: string;
  file_size: number;
  uploaded_by: string;
  uploaded_at: string;
}
