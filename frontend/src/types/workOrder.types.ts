/**
 * Work Order types
 */

export type WorkOrderType = 'CORRECTIVE' | 'PREVENTIVE' | 'PREDICTIVE' | 'INSPECTION';
export type WorkOrderPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
export type WorkOrderStatus = 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface WorkOrder {
  id: string;
  work_order_number: string;
  title: string;
  description: string;
  
  // Asset fields can be null if no asset is assigned to the work order
  // This can happen when:
  // - Work order is created without an asset (e.g., general maintenance tasks)
  // - Asset was deleted but work order still exists
  // - Work order is pending asset assignment
  asset: string | null;
  asset_name: string | null;
  asset_code: string | null;
  
  work_order_type: WorkOrderType;
  work_order_type_display: string;
  priority: WorkOrderPriority;
  priority_display: string;
  status: WorkOrderStatus;
  status_display: string;
  assigned_to?: string;
  assigned_to_name?: string;
  created_by: string;
  created_by_name: string;
  scheduled_date?: string;
  started_at?: string;
  completed_at?: string;
  estimated_hours?: number;
  actual_hours?: number;
  completion_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkOrderFormData {
  title: string;
  description: string;
  asset: string | null; // Asset can be null when creating work orders without equipment
  work_order_type: WorkOrderType;
  priority: WorkOrderPriority;
  assigned_to?: string;
  scheduled_date?: string;
  estimated_hours?: number;
}

export interface WorkOrderCompleteData {
  actual_hours: number;
  completion_notes: string;
}

export interface WorkOrderStatusChange {
  status: WorkOrderStatus;
  notes?: string;
}
