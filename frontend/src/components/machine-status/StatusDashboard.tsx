import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MachineStatus } from '../../types/machineStatus.types';
import machineStatusService from '../../services/machineStatusService';
import { toast } from 'react-hot-toast';

const StatusDashboard = () => {
  const navigate = useNavigate();
  const [statuses, setStatuses] = useState<MachineStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    fetchStatuses();
  }, [filterStatus]);

  const fetchStatuses = async () => {
    try {
      setLoading(true);
      const data = await machineStatusService.getAll({
        status_type: filterStatus || undefined,
      });
      setStatuses(data);
    } catch (error) {
      console.error('Error fetching statuses:', error);
      toast.error('Error al cargar estados');
    } finally {
      setLoading(false);
    }
  };

  const filteredStatuses = statuses.filter((status) =>
    status.asset_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    status.asset_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (statusType: string) => {
    const statusMap: Record<string, { className: string }> = {
      OPERANDO: { className: 'bg-green-100 text-green-800' },
      DETENIDA: { className: 'bg-yellow-100 text-yellow-800' },
      EN_MANTENIMIENTO: { className: 'bg-blue-100 text-blue-800' },
      FUERA_DE_SERVICIO: { className: 'bg-red-100 text-red-800' },
    };
    const config = statusMap[statusType] || statusMap.OPERANDO;
    return config.className;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Estado de Máquinas</h2>
        <Link
          to="/machine-status/new"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          + Actualizar Estado
        </Link>
      </div>

      {/* Search and Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Buscar por nombre o código de activo..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Todos los estados</option>
          <option value="OPERANDO">Operando</option>
          <option value="DETENIDA">Detenida</option>
          <option value="EN_MANTENIMIENTO">En Mantenimiento</option>
          <option value="FUERA_DE_SERVICIO">Fuera de Servicio</option>
        </select>
      </div>

      {/* Status Table */}
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Activo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Odómetro
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Combustible
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reportado por
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredStatuses.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                  No se encontraron registros de estado
                </td>
              </tr>
            ) : (
              filteredStatuses.map((status) => (
                <tr key={status.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{status.asset_name}</div>
                    <div className="text-sm text-gray-500">{status.asset_code}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(status.status_type)}`}>
                      {status.status_display}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {status.odometer_reading ? status.odometer_reading.toFixed(2) : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {status.fuel_level !== null && status.fuel_level !== undefined ? (
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${status.fuel_level}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{status.fuel_level}%</span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {status.reported_by_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(status.reported_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => navigate(`/machine-status/history/${status.asset}`)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      📊 Ver Historial
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StatusDashboard;
