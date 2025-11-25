/**
 * Prediction Service
 */
import api from './api';
import {
  FailurePrediction,
  Alert,
  HealthDashboard,
  PredictionTrend,
} from '../types/prediction.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const predictionService = {
  // Predictions
  getPredictions: async (params?: {
    asset?: string;
    risk_level?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<FailurePrediction>> => {
    const response = await api.get('/predictions/predictions/', { params });
    return response.data;
  },

  getPrediction: async (id: string): Promise<FailurePrediction> => {
    const response = await api.get(`/predictions/predictions/${id}/`);
    return response.data;
  },

  getHighRiskPredictions: async (): Promise<FailurePrediction[]> => {
    const response = await api.get('/predictions/predictions/high_risk/');
    return response.data;
  },

  predictAsset: async (assetId: string): Promise<FailurePrediction> => {
    const response = await api.post('/predictions/predictions/predict_asset/', {
      asset_id: assetId,
    });
    return response.data;
  },

  predictAllAssets: async (): Promise<{ count: number; predictions: FailurePrediction[] }> => {
    const response = await api.post('/predictions/predictions/predict_all_assets/');
    return response.data;
  },

  getHealthDashboard: async (): Promise<HealthDashboard> => {
    const response = await api.get('/predictions/predictions/asset_health_dashboard/');
    return response.data;
  },

  getPredictionTrends: async (days: number = 30): Promise<PredictionTrend[]> => {
    const response = await api.get('/predictions/predictions/prediction_trends/', {
      params: { days },
    });
    return response.data;
  },

  // Alerts
  getAlerts: async (params?: {
    alert_type?: string;
    severity?: string;
    is_read?: boolean;
    is_resolved?: boolean;
    ordering?: string;
  }): Promise<PaginatedResponse<Alert>> => {
    const response = await api.get('/predictions/alerts/', { params });
    return response.data;
  },

  getAlert: async (id: string): Promise<Alert> => {
    const response = await api.get(`/predictions/alerts/${id}/`);
    return response.data;
  },

  getUnreadAlerts: async (): Promise<Alert[]> => {
    const response = await api.get('/predictions/alerts/unread/');
    return response.data;
  },

  getCriticalAlerts: async (): Promise<Alert[]> => {
    const response = await api.get('/predictions/alerts/critical/');
    return response.data;
  },

  markAlertAsRead: async (id: string): Promise<Alert> => {
    const response = await api.post(`/predictions/alerts/${id}/mark_read/`);
    return response.data;
  },

  resolveAlert: async (id: string): Promise<Alert> => {
    const response = await api.post(`/predictions/alerts/${id}/resolve/`);
    return response.data;
  },

  getAlertStats: async (): Promise<{
    total: number;
    unread: number;
    unresolved: number;
    critical: number;
  }> => {
    const response = await api.get('/predictions/alerts/stats/');
    return response.data;
  },

  // New Dashboard endpoints
  getDashboardStats: async (): Promise<{
    total_assets_monitored: number;
    average_failure_probability: number;
    high_risk_assets: number;
    risk_distribution: Record<string, number>;
    last_updated: string | null;
  }> => {
    const response = await api.get('/predictions/predictions/dashboard_stats/');
    return response.data;
  },

  getTrendingRisks: async (): Promise<{
    trending_assets: Array<{
      asset_id: string;
      asset_name: string;
      asset_code: string;
      current_probability: number;
      trend: number;
      trend_direction: 'increasing' | 'decreasing' | 'stable';
      prediction_count: number;
    }>;
    analysis_period_days: number;
    total_assets_analyzed: number;
  }> => {
    const response = await api.get('/predictions/predictions/trending_risks/');
    return response.data;
  },

  batchPredict: async (assetIds: string[]): Promise<{
    predictions: FailurePrediction[];
    errors: Array<{ asset_id: string; error: string }>;
    total_processed: number;
    successful: number;
    failed: number;
  }> => {
    const response = await api.post('/predictions/predictions/batch_predict/', {
      asset_ids: assetIds,
    });
    return response.data;
  },

  // ML Model Management
  getModelStatus: async (): Promise<{
    vertex_ai: any;
    local_model: {
      loaded: boolean;
      version: string;
      features: string[];
    };
    status: string;
  }> => {
    const response = await api.get('/predictions/ml-model/status/');
    return response.data;
  },

  trainModel: async (): Promise<{
    message: string;
    metrics: any;
    model_path: string;
    version: string;
  }> => {
    const response = await api.post('/predictions/ml-model/train/');
    return response.data;
  },

  testPrediction: async (assetId: string, useVertexAI: boolean = false): Promise<{
    asset_id: string;
    asset_name: string;
    prediction: any;
    test_mode: boolean;
  }> => {
    const response = await api.post('/predictions/ml-model/test_prediction/', {
      asset_id: assetId,
      use_vertex_ai: useVertexAI,
    });
    return response.data;
  },
};

export default predictionService;
