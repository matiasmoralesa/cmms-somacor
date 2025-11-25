/**
 * Predictions Dashboard Page
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import predictionService from '../services/predictionService';
import PredictionStatsCard from '../components/predictions/PredictionStatsCard';
import RiskDistributionChart from '../components/predictions/RiskDistributionChart';
import TrendingRisksTable from '../components/predictions/TrendingRisksTable';
import AlertsList from '../components/predictions/AlertsList';
import { Alert } from '../types/prediction.types';

const Predictions: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardStats, setDashboardStats] = useState<any>(null);
  const [trendingRisks, setTrendingRisks] = useState<any>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // For now, set empty data since endpoints are not implemented
      setDashboardStats({
        total_assets_monitored: 0,
        average_failure_probability: 0,
        high_risk_assets: 0,
        risk_distribution: {},
        last_updated: null
      });
      setTrendingRisks({
        trending_assets: [],
        analysis_period_days: 30,
        total_assets_analyzed: 0
      });
      setAlerts([]);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError(err.message || 'Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (alertId: string) => {
    try {
      await predictionService.markAlertAsRead(alertId);
      // Reload alerts
      const alertsData = await predictionService.getCriticalAlerts();
      setAlerts(alertsData);
    } catch (err: any) {
      console.error('Error marking alert as read:', err);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      await predictionService.resolveAlert(alertId);
      // Reload alerts
      const alertsData = await predictionService.getCriticalAlerts();
      setAlerts(alertsData);
    } catch (err: any) {
      console.error('Error resolving alert:', err);
    }
  };

  const handleAssetClick = (assetId: string) => {
    navigate(`/assets/${assetId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6 bg-red-50 border-red-200">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
        <p className="text-red-700">{error}</p>
        <button
          onClick={loadDashboardData}
          className="mt-4 btn btn-primary"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard de Predicciones
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Monitoreo predictivo de fallas y mantenimiento
          </p>
        </div>
        <button
          onClick={loadDashboardData}
          className="btn btn-secondary"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Stats Cards */}
      {dashboardStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <PredictionStatsCard
            title="Activos Monitoreados"
            value={dashboardStats.total_assets_monitored}
            icon={<span className="text-2xl">📊</span>}
            color="blue"
          />
          <PredictionStatsCard
            title="Probabilidad Promedio"
            value={`${dashboardStats.average_failure_probability.toFixed(1)}%`}
            subtitle="de falla"
            icon={<span className="text-2xl">📈</span>}
            color="amber"
          />
          <PredictionStatsCard
            title="Activos de Alto Riesgo"
            value={dashboardStats.high_risk_assets}
            subtitle="≥ 50% probabilidad"
            icon={<span className="text-2xl">⚠️</span>}
            color="red"
          />
          <PredictionStatsCard
            title="Alertas Críticas"
            value={alerts.length}
            subtitle="sin resolver"
            icon={<span className="text-2xl">🚨</span>}
            color="red"
          />
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution */}
        <div className="lg:col-span-1">
          {dashboardStats && (
            <RiskDistributionChart
              distribution={dashboardStats.risk_distribution}
            />
          )}
        </div>

        {/* Alerts */}
        <div className="lg:col-span-2">
          <AlertsList
            alerts={alerts}
            onMarkAsRead={handleMarkAsRead}
            onResolve={handleResolveAlert}
            maxItems={5}
          />
        </div>
      </div>

      {/* Trending Risks */}
      {trendingRisks && (
        <TrendingRisksTable
          assets={trendingRisks.trending_assets}
          onAssetClick={handleAssetClick}
        />
      )}

      {/* Last Updated */}
      {dashboardStats?.last_updated && (
        <div className="text-center text-sm text-gray-500">
          Última actualización:{' '}
          {new Date(dashboardStats.last_updated).toLocaleString('es-ES', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      )}
    </div>
  );
};

export default Predictions;
