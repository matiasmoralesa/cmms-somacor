/**
 * TypeScript types for predictions
 */

export interface FailurePrediction {
  id: string;
  asset: string;
  asset_name: string;
  asset_code: string;
  prediction_date: string;
  failure_probability: number;
  predicted_failure_date: string | null;
  confidence_score: number;
  model_version: string;
  input_features: Record<string, any>;
  recommendations: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_level_display: string;
  created_at: string;
}

export interface Alert {
  id: string;
  alert_type: 'PREDICTION' | 'LOW_STOCK' | 'OVERDUE_MAINTENANCE' | 'SYSTEM';
  alert_type_display: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  severity_display: string;
  title: string;
  message: string;
  asset: string | null;
  asset_name: string | null;
  work_order: string | null;
  prediction: string | null;
  is_read: boolean;
  is_resolved: boolean;
  resolved_by: string | null;
  resolved_by_name: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface AssetHealthScore {
  asset_id: string;
  asset_name: string;
  asset_code: string;
  vehicle_type: string;
  health_score: number;
  failure_probability: number;
  risk_level: string;
  risk_level_display: string;
  last_prediction: string;
  predicted_failure_date: string | null;
}

export interface HealthDashboard {
  summary: {
    total_assets: number;
    average_health_score: number;
    critical_risk: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
  };
  assets: AssetHealthScore[];
}

export interface PredictionTrend {
  date: string;
  avg_probability: number;
  count: number;
  critical_count: number;
  high_count: number;
}
