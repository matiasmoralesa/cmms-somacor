/**
 * Dashboard Service
 * Obtiene estadísticas y datos del dashboard desde el backend
 */
import api from './api';

export interface DashboardStats {
  active_work_orders: number;
  operational_assets: number;
  pending_maintenance: number;
  critical_alerts: number;
  work_orders_change: string;
  assets_change: string;
  maintenance_change: string;
  alerts_change: string;
}

export interface MaintenanceTrend {
  month: string;
  preventivo: number;
  correctivo: number;
  predictivo: number;
}

export interface WorkOrdersByPriority {
  priority: string;
  count: number;
}

export interface AssetHealth {
  name: string;
  value: number;
  color: string;
}

export interface DashboardData {
  stats: DashboardStats;
  maintenance_trend: MaintenanceTrend[];
  work_orders_by_priority: WorkOrdersByPriority[];
  asset_health: AssetHealth[];
}

const dashboardService = {
  /**
   * Obtiene todos los datos del dashboard
   */
  async getDashboardData(): Promise<DashboardData> {
    const response = await api.get('/reports/dashboard_summary/');
    return response.data;
  },

  /**
   * Obtiene solo las estadísticas principales
   */
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/dashboard/stats/');
    return response.data;
  },

  /**
   * Obtiene tendencia de mantenimientos
   */
  async getMaintenanceTrend(): Promise<MaintenanceTrend[]> {
    const response = await api.get('/dashboard/maintenance-trend/');
    return response.data;
  },

  /**
   * Obtiene órdenes de trabajo por prioridad
   */
  async getWorkOrdersByPriority(): Promise<WorkOrdersByPriority[]> {
    const response = await api.get('/dashboard/work-orders-by-priority/');
    return response.data;
  },

  /**
   * Obtiene estado de salud de activos
   */
  async getAssetHealth(): Promise<AssetHealth[]> {
    const response = await api.get('/dashboard/asset-health/');
    return response.data;
  },
};

export default dashboardService;
