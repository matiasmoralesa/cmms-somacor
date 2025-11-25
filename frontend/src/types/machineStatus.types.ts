export interface MachineStatus {
  id: string;
  asset: string;
  asset_name: string;
  asset_code: string;
  status_type: 'OPERANDO' | 'DETENIDA' | 'EN_MANTENIMIENTO' | 'FUERA_DE_SERVICIO';
  status_display: string;
  odometer_reading?: number;
  fuel_level?: number;
  condition_notes?: string;
  location?: string;
  location_name?: string;
  reported_by: string;
  reported_by_name: string;
  reported_at: string;
}

export interface MachineStatusFormData {
  asset: string;
  status_type: 'OPERANDO' | 'DETENIDA' | 'EN_MANTENIMIENTO' | 'FUERA_DE_SERVICIO';
  odometer_reading?: number;
  fuel_level?: number;
  condition_notes?: string;
  location?: string;
}

export interface StatusHistory {
  id: string;
  asset: string;
  asset_name: string;
  previous_status?: string;
  new_status: string;
  previous_odometer?: number;
  new_odometer?: number;
  changed_by: string;
  changed_by_name: string;
  changed_at: string;
  change_reason?: string;
}

export interface ChartData {
  labels: string[];
  odometer: (number | null)[];
  fuel_level: (number | null)[];
  status_timeline: {
    date: string;
    status: string;
    status_display: string;
  }[];
}

export interface StatusDistribution {
  status_type: string;
  count: number;
}
