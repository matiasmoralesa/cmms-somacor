/**
 * Checklist Types
 */

export interface ChecklistItem {
  section: string;
  order: number;
  question: string;
  response_type: 'yes_no_na';
  required: boolean;
  observations_allowed: boolean;
}

export interface ChecklistTemplate {
  id: string;
  code: string;
  name: string;
  vehicle_type: string;
  vehicle_type_display: string;
  description: string;
  items: ChecklistItem[];
  is_system_template: boolean;
  passing_score: number;
  item_count: number;
  response_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChecklistResponseItem {
  item_order: number;
  response: 'yes' | 'no' | 'na';
  notes?: string;
  photo_url?: string;
}

export interface ChecklistResponse {
  id: string;
  template: string;
  template_code: string;
  template_name: string;
  work_order?: string;
  work_order_number?: string;
  asset: string;
  asset_name: string;
  asset_code: string;
  responses: ChecklistResponseItem[];
  score: number;
  passed: boolean;
  pdf_url?: string;
  signature_url?: string;
  completed_by: string;
  completed_by_name: string;
  completed_at: string;
  operator_name: string;
  shift?: string;
  odometer_reading?: number;
}

export interface ChecklistResponseCreate {
  template: string;
  asset: string;
  work_order?: string;
  responses: ChecklistResponseItem[];
  operator_name: string;
  shift?: string;
  odometer_reading?: number;
  signature_url?: string;
}

export interface ChecklistStatistics {
  total: number;
  passed: number;
  failed: number;
  average_score: number;
  by_template: {
    [key: string]: {
      name: string;
      count: number;
      passed: number;
      failed: number;
    };
  };
}
