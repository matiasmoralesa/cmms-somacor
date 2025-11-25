/**
 * TypeScript types for notifications
 */

export type NotificationType =
  | 'WORK_ORDER_CREATED'
  | 'WORK_ORDER_ASSIGNED'
  | 'WORK_ORDER_COMPLETED'
  | 'MAINTENANCE_DUE'
  | 'LOW_STOCK'
  | 'PREDICTION_HIGH_RISK'
  | 'SYSTEM';

export type NotificationPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Notification {
  id: string;
  user: string;
  notification_type: NotificationType;
  notification_type_display: string;
  priority: NotificationPriority;
  priority_display: string;
  title: string;
  message: string;
  work_order: string | null;
  work_order_number: string | null;
  asset: string | null;
  asset_name: string | null;
  prediction: string | null;
  data: Record<string, any>;
  is_read: boolean;
  read_at: string | null;
  pubsub_message_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreference {
  id: string;
  user: string;
  notification_type: NotificationType;
  notification_type_display: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  push_enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationStats {
  count: number;
}
