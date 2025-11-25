/**
 * Inventory Type Definitions
 */

export interface SparePart {
  id: string;
  part_number: string;
  name: string;
  description?: string;
  category: string;
  quantity: number;
  minimum_stock: number;
  unit_cost: number;
  location: string;
  supplier?: string;
  compatible_assets?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface StockMovement {
  id: string;
  spare_part: string;
  spare_part_name?: string;
  movement_type: string;
  movement_type_display?: string;
  quantity: number;
  work_order?: string;
  work_order_number?: string;
  performed_by: string;
  performed_by_name?: string;
  notes?: string;
  created_at: string;
}
