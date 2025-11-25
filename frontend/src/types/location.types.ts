export interface Location {
  id: string;
  name: string;
  address?: string;
  city?: string;
  region?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  asset_count: number;
  can_delete: boolean;
}

export interface LocationListItem {
  id: string;
  name: string;
  city?: string;
  region?: string;
  is_active: boolean;
  asset_count: number;
}

export interface LocationFormData {
  name: string;
  address?: string;
  city?: string;
  region?: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  description?: string;
  is_active: boolean;
}
