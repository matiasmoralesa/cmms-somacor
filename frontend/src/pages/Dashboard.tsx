/**
 * Modern Dashboard Page
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import dashboardService, { DashboardData } from '../services/dashboardService';
import LineChart from '../components/charts/LineChart';
import BarChart from '../components/charts/BarChart';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getDashboardData();
      setDashboardData(data);
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      setError('Error al cargar los datos del dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Determinar tipo de cambio basado en el valor
  const getChangeType = (change: string): 'positive' | 'negative' => {
    return change.startsWith('+') || change.startsWith('-') && parseFloat(change) < 0 ? 'positive' : 'negative';
  };

  const stats = dashboardData ? [
    {
      name: 'Órdenes Activas',
      value: dashboardData.stats.active_work_orders.toString(),
      change: dashboardData.stats.work_orders_change,
      changeType: getChangeType(dashboardData.stats.work_orders_change),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
      ),
      color: 'blue',
    },
    {
      name: 'Activos Operativos',
      value: dashboardData.stats.operational_assets.toString(),
      change: dashboardData.stats.assets_change,
      changeType: getChangeType(dashboardData.stats.assets_change),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          />
        </svg>
      ),
      color: 'green',
    },
    {
      name: 'Mantenimientos Pendientes',
      value: dashboardData.stats.pending_maintenance.toString(),
      change: dashboardData.stats.maintenance_change,
      changeType: 'negative',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      color: 'amber',
    },
    {
      name: 'Alertas Críticas',
      value: dashboardData.stats.critical_alerts.toString(),
      change: dashboardData.stats.alerts_change,
      changeType: 'negative',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      ),
      color: 'red',
    },
  ] : [];

  // Calcular total de activos para porcentajes
  const totalAssets = dashboardData?.asset_health.reduce((sum, item) => sum + item.value, 0) || 1;

  const modules = [
    {
      name: 'Checklists',
      description: 'Gestiona y completa checklists de inspección para vehículos',
      path: '/checklists',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      ),
      color: 'blue',
      available: true,
    },
    {
      name: 'Activos',
      description: 'Gestiona la flota de vehículos y equipos',
      path: '/assets',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          />
        </svg>
      ),
      color: 'green',
      available: true,
    },
    {
      name: 'Órdenes de Trabajo',
      description: 'Gestiona órdenes de trabajo y asignaciones',
      path: '/work-orders',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
          />
        </svg>
      ),
      color: 'purple',
      available: true,
    },
    {
      name: 'Mantenimiento',
      description: 'Planifica y programa mantenimientos preventivos',
      path: '/maintenance',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      ),
      color: 'amber',
      available: true,
    },
    {
      name: 'Inventario',
      description: 'Control de repuestos y materiales',
      path: '/inventory',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
          />
        </svg>
      ),
      color: 'indigo',
      available: true,
    },
    {
      name: 'Reportes',
      description: 'Análisis y reportes de gestión',
      path: '/reports',
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
      color: 'pink',
      available: true,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section - Premium Design */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 p-8 shadow-2xl shadow-blue-500/30">
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 bg-grid-white/[0.05] bg-[size:20px_20px]" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-indigo-500/20 rounded-full blur-3xl" />
        
        <div className="relative flex items-center justify-between">
          <div className="flex-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-sm rounded-full mb-4">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm text-white/90 font-medium">En línea</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold mb-2 text-white">
              ¡Bienvenido, {user?.first_name}! 👋
            </h1>
            <p className="text-blue-100 text-lg flex items-center gap-2">
              <span className="px-3 py-1 bg-white/10 backdrop-blur-sm rounded-lg font-medium">
                {user?.role_display}
              </span>
              <span className="text-blue-200">•</span>
              <span>{user?.email}</span>
            </p>
          </div>
          <div className="hidden lg:block">
            <div className="w-24 h-24 bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-xl border border-white/20">
              <svg
                className="w-14 h-14 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </div>
          </div>
        </div>

        {/* License Warning */}
        {user?.role === 'OPERADOR' && user?.license_status && !user.license_status.valid && (
          <div className="relative mt-6 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 backdrop-blur-sm border border-yellow-300/30 rounded-2xl p-5 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-yellow-400/20 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-yellow-200"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-white text-lg">Atención: Licencia Vencida</p>
                <p className="text-sm text-blue-100 mt-1">
                  Por favor, actualiza tu licencia para continuar operando vehículos
                </p>
              </div>
            </div>
          </div>
        )}

        {user?.role === 'OPERADOR' && user?.license_status?.expires_soon && user.license_status.valid && (
          <div className="relative mt-6 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 backdrop-blur-sm border border-yellow-300/30 rounded-2xl p-5 shadow-lg">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 bg-yellow-400/20 rounded-xl flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-yellow-200"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-white text-lg">Licencia por Vencer</p>
                <p className="text-sm text-blue-100 mt-1">
                  Tu licencia vence en {user.license_status.days_until_expiration} días
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-red-800">{error}</p>
          <button onClick={loadDashboardData} className="mt-2 text-sm text-red-600 hover:text-red-700 font-medium">
            Reintentar
          </button>
        </div>
      )}

      {/* Stats Grid - Enhanced Design */}
      {!loading && !error && dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
          <div 
            key={stat.name} 
            className="stat-card group"
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="stat-label">{stat.name}</p>
                <p className="stat-value mt-2">{stat.value}</p>
                <div className="flex items-center gap-2 mt-3">
                  <span
                    className={`stat-change ${
                      stat.changeType === 'positive'
                        ? 'stat-change-positive'
                        : 'stat-change-negative'
                    }`}
                  >
                    {stat.changeType === 'positive' ? (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    )}
                    {stat.change}
                  </span>
                  <span className="text-xs text-gray-500">vs mes anterior</span>
                </div>
              </div>
              <div
                className={`w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br shadow-lg transition-transform duration-300 group-hover:scale-110 ${
                  stat.color === 'blue' ? 'from-blue-500 to-blue-600 shadow-blue-500/30' :
                  stat.color === 'green' ? 'from-green-500 to-green-600 shadow-green-500/30' :
                  stat.color === 'amber' ? 'from-amber-500 to-amber-600 shadow-amber-500/30' :
                  'from-red-500 to-red-600 shadow-red-500/30'
                }`}
              >
                <div className="text-white">
                  {stat.icon}
                </div>
              </div>
            </div>
            </div>
          ))}
        </div>
      )}

      {/* Charts Section */}
      {!loading && !error && dashboardData && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Maintenance Trend Chart */}
            <div className="card">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Tendencia de Mantenimientos
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Últimos 6 meses
                </p>
              </div>
              <div className="p-6">
                <LineChart
                  data={dashboardData.maintenance_trend}
                  dataKeys={[
                    { key: 'preventivo', color: '#22c55e', name: 'Preventivo' },
                    { key: 'correctivo', color: '#ef4444', name: 'Correctivo' },
                    { key: 'predictivo', color: '#3b82f6', name: 'Predictivo' },
                  ]}
                  xAxisKey="month"
                  height={280}
                />
              </div>
            </div>

            {/* Work Orders by Priority */}
            <div className="card">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">
                  Órdenes de Trabajo por Prioridad
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  Distribución actual
                </p>
              </div>
              <div className="p-6">
                <BarChart
                  data={dashboardData.work_orders_by_priority}
                  dataKeys={[
                    { key: 'count', color: '#3b82f6', name: 'Cantidad' },
                  ]}
                  xAxisKey="priority"
                  height={280}
                />
              </div>
            </div>
          </div>

          {/* Asset Health Overview */}
          <div className="card">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Estado General de Activos
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-3 gap-6">
                {dashboardData.asset_health.map((item) => (
                  <div key={item.name} className="text-center">
                    <div
                      className="w-24 h-24 mx-auto rounded-full flex items-center justify-center text-2xl font-bold text-white mb-3"
                      style={{ backgroundColor: item.color }}
                    >
                      {item.value}
                    </div>
                    <p className="text-sm font-medium text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {((item.value / totalAssets) * 100).toFixed(1)}% del total
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Modules Section */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Módulos del Sistema
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => (
            <button
              key={module.name}
              onClick={() => module.available && navigate(module.path)}
              disabled={!module.available}
              className={`card p-6 text-left transition-all ${
                module.available
                  ? 'card-hover cursor-pointer'
                  : 'opacity-50 cursor-not-allowed'
              }`}
            >
              <div
                className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 bg-${module.color}-100 text-${module.color}-600`}
              >
                {module.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {module.name}
              </h3>
              <p className="text-sm text-gray-600 mb-4">{module.description}</p>
              {module.available ? (
                <div className={`text-sm font-medium text-${module.color}-600 flex items-center gap-2`}>
                  <span>Ir al módulo</span>
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              ) : (
                <div className="text-sm text-gray-400">Próximamente...</div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
