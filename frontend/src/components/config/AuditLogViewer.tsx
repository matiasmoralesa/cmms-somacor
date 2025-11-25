/**
 * Audit Log Viewer Component
 */
import React, { useState, useEffect } from 'react';
import { getAuditLogs, AuditLog } from '../../services/configService';

const AuditLogViewer: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    model_name: '',
    action: '',
    user: ''
  });
  const [expandedLog, setExpandedLog] = useState<string | null>(null);

  useEffect(() => {
    loadLogs();
  }, [filters]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filters.model_name) params.model_name = filters.model_name;
      if (filters.action) params.action = filters.action;
      if (filters.user) params.user = filters.user;

      const data = await getAuditLogs(params);
      setLogs(data.results || data);
    } catch (err) {
      console.error('Error loading audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('es-CL', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActionBadge = (action: string) => {
    const styles = {
      CREATE: 'bg-green-100 text-green-800',
      UPDATE: 'bg-blue-100 text-blue-800',
      DELETE: 'bg-red-100 text-red-800'
    };
    return styles[action as keyof typeof styles] || 'bg-gray-100 text-gray-800';
  };

  const getActionLabel = (action: string) => {
    const labels = {
      CREATE: 'Creación',
      UPDATE: 'Actualización',
      DELETE: 'Eliminación'
    };
    return labels[action as keyof typeof labels] || action;
  };

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Registro de Auditoría</h2>

      {/* Filters */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Modelo</label>
          <input
            type="text"
            value={filters.model_name}
            onChange={(e) => setFilters({ ...filters, model_name: e.target.value })}
            className="input"
            placeholder="Ej: assets.Asset"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Acción</label>
          <select
            value={filters.action}
            onChange={(e) => setFilters({ ...filters, action: e.target.value })}
            className="input"
          >
            <option value="">Todas</option>
            <option value="CREATE">Creación</option>
            <option value="UPDATE">Actualización</option>
            <option value="DELETE">Eliminación</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
          <input
            type="text"
            value={filters.user}
            onChange={(e) => setFilters({ ...filters, user: e.target.value })}
            className="input"
            placeholder="ID de usuario"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No se encontraron registros de auditoría
        </div>
      ) : (
        <div className="space-y-3">
          {logs.map((log) => (
            <div key={log.id} className="card p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionBadge(log.action)}`}>
                      {getActionLabel(log.action)}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{log.model_name}</span>
                    <span className="text-sm text-gray-500">•</span>
                    <span className="text-sm text-gray-600">{log.object_repr}</span>
                  </div>

                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>
                      👤 {log.user ? `${log.user.first_name} ${log.user.last_name}` : 'Sistema'}
                    </span>
                    <span>🕐 {formatDate(log.timestamp)}</span>
                    {log.ip_address && <span>🌐 {log.ip_address}</span>}
                  </div>

                  {/* Changes Details */}
                  {Object.keys(log.changes).length > 0 && (
                    <div className="mt-3">
                      <button
                        onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                        className="text-sm text-blue-600 hover:text-blue-800"
                      >
                        {expandedLog === log.id ? '▼ Ocultar cambios' : '▶ Ver cambios'}
                      </button>

                      {expandedLog === log.id && (
                        <div className="mt-2 p-3 bg-gray-50 rounded text-sm">
                          <pre className="whitespace-pre-wrap font-mono text-xs">
                            {JSON.stringify(log.changes, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuditLogViewer;
