import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import machineStatusService from '../../services/machineStatusService';
import { toast } from 'react-hot-toast';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

const StatusHistory = () => {
  const { assetId } = useParams<{ assetId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState<any>(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    if (assetId) {
      fetchChartData();
    }
  }, [assetId, days]);

  const fetchChartData = async () => {
    try {
      setLoading(true);
      const data = await machineStatusService.getChartData(assetId!, days);
      setChartData(data);
    } catch (error) {
      console.error('Error fetching chart data:', error);
      toast.error('Error al cargar datos del historial');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      toast.loading('Generando informe...');
      const blob = await machineStatusService.downloadMaintenanceReport(assetId!);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `mantenimiento_${chartData?.asset?.asset_code}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.dismiss();
      toast.success('Informe descargado exitosamente');
    } catch (error) {
      toast.dismiss();
      console.error('Error downloading report:', error);
      toast.error('Error al descargar informe');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!chartData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay datos disponibles</p>
      </div>
    );
  }

  // Prepare data for charts
  const odometerData = chartData.chart_data.labels.map((label: string, index: number) => ({
    date: label,
    odometer: chartData.chart_data.odometer[index],
  })).filter((d: any) => d.odometer !== null);

  const fuelData = chartData.chart_data.labels.map((label: string, index: number) => ({
    date: label,
    fuel: chartData.chart_data.fuel_level[index],
  })).filter((d: any) => d.fuel !== null);

  const statusDistData = chartData.status_distribution.map((item: any) => ({
    name: item.status_type,
    value: item.count,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Historial de Estado: {chartData.asset.name}
          </h2>
          <p className="text-sm text-gray-500">Código: {chartData.asset.asset_code}</p>
        </div>
        <div className="flex gap-2">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={7}>Últimos 7 días</option>
            <option value={30}>Últimos 30 días</option>
            <option value={90}>Últimos 90 días</option>
            <option value={180}>Últimos 6 meses</option>
          </select>
          <button
            onClick={handleDownloadReport}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            📄 Generar Informe PDF
          </button>
          <button
            onClick={() => navigate('/machine-status')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
          >
            Volver
          </button>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Odometer Chart */}
        {odometerData.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Lectura de Odómetro/Horómetro</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={odometerData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="odometer" stroke="#3b82f6" name="Odómetro" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Fuel Level Chart */}
        {fuelData.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Nivel de Combustible (%)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={fuelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="fuel" stroke="#10b981" name="Combustible %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Status Distribution */}
        {statusDistData.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Distribución de Estados</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusDistData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Status Timeline */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-lg font-semibold mb-4">Línea de Tiempo de Estados</h3>
          <div className="space-y-2 max-h-[300px] overflow-y-auto">
            {chartData.chart_data.status_timeline.map((item: any, index: number) => (
              <div key={index} className="flex items-center gap-3 p-2 border-l-4 border-blue-500 bg-gray-50">
                <div className="text-xs text-gray-500 w-32">
                  {new Date(item.date).toLocaleString()}
                </div>
                <div className="flex-1">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    item.status === 'OPERANDO' ? 'bg-green-100 text-green-800' :
                    item.status === 'DETENIDA' ? 'bg-yellow-100 text-yellow-800' :
                    item.status === 'EN_MANTENIMIENTO' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {item.status_display}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusHistory;
