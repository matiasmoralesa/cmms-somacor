/**
 * Reports Dashboard Page
 */
import React, { useState, useEffect } from 'react';
import reportService from '../services/reportService';

const Reports: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    loadDashboardData();
  }, [dateRange]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await reportService.getDashboardSummary(dateRange);
      setDashboardData(data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (reportType: string) => {
    try {
      const blob = await reportService.exportCSV(reportType, dateRange);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_${dateRange.start_date}_${dateRange.end_date}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting report:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Cargando reportes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reportes y Análisis</h1>
          <p className="mt-1 text-sm text-gray-600">
            Métricas y reportes del sistema CMMS
          </p>
        </div>
      </div>

      {/* Date Range Picker */}
      <div className="card p-4">
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Inicio
            </label>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fecha Fin
            </label>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="pt-6">
            <button onClick={loadDashboardData} className="btn btn-primary">
              Actualizar
            </button>
          </div>
        </div>
      </div>

      {dashboardData && (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Órdenes</p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900">
                    {dashboardData.work_orders.total}
                  </p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <span className="text-2xl">📋</span>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">MTTR Promedio</p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900">
                    {dashboardData.mttr.avg_repair_hours?.toFixed(1) || 0}h
                  </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <span className="text-2xl">⏱️</span>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Horas</p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900">
                    {dashboardData.work_orders.total_hours?.toFixed(0) || 0}h
                  </p>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg">
                  <span className="text-2xl">🔧</span>
                </div>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Reparaciones</p>
                  <p className="mt-2 text-3xl font-semibold text-gray-900">
                    {dashboardData.mttr.total_repairs || 0}
                  </p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <span className="text-2xl">🛠️</span>
                </div>
              </div>
            </div>
          </div>

          {/* Charts and Tables */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Downtime Assets */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Activos con Mayor Tiempo Fuera de Servicio
                </h3>
                <button
                  onClick={() => handleExport('asset_downtime')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Exportar CSV
                </button>
              </div>
              <div className="space-y-3">
                {dashboardData.top_downtime_assets.map((asset: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{asset.asset__name}</p>
                      <p className="text-xs text-gray-500">{asset.asset__asset_code}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {asset.total_downtime_hours?.toFixed(1)}h
                      </p>
                      <p className="text-xs text-gray-500">
                        {asset.work_order_count} órdenes
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Consumed Parts */}
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Repuestos Más Consumidos
                </h3>
                <button
                  onClick={() => handleExport('spare_part_consumption')}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Exportar CSV
                </button>
              </div>
              <div className="space-y-3">
                {dashboardData.top_consumed_parts.map((part: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{part.spare_part__name}</p>
                      <p className="text-xs text-gray-500">{part.spare_part__part_number}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {part.total_quantity} unidades
                      </p>
                      <p className="text-xs text-gray-500">
                        {part.movement_count} movimientos
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Work Orders by Status */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Órdenes de Trabajo por Estado
              </h3>
              <button
                onClick={() => handleExport('work_orders_summary')}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Exportar CSV
              </button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(dashboardData.work_orders.by_status).map(([status, count]: [string, any]) => (
                <div key={status} className="p-4 bg-gray-50 rounded-lg text-center">
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                  <p className="text-sm text-gray-600 mt-1">{status}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Reports;
