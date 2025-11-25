/**
 * Maintenance Type Definitions
 */

export interface MaintenancePlan {
  id: string;
  name: string;
  asset: string;
  asset_name?: string;
  asset_code?: string;
  plan_type: string;
  plan_type_display?: string;
  recurrence_type: string;
  recurrence_type_display?: string;
  recurrence_interval: number;
  next_due_date: string;
  is_active: boolean;
  checklist_template?: string;
  checklist_template_name?: string;
  estimated_duration: number;
  created_by?: string;
  created_by_name?: string;
  created_at?: string;
  updated_at?: string;
}
