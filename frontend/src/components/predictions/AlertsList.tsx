/**
 * Alerts List Component
 */
import React from 'react';
import { Alert } from '../../types/prediction.types';

interface AlertsListProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
  onMarkAsRead?: (alertId: string) => void;
  onResolve?: (alertId: string) => void;
  maxItems?: number;
}

const AlertsList: React.FC<AlertsListProps> = ({
  alerts,
  onAlertClick,
  onMarkAsRead,
  onResolve,
  maxItems,
}) => {
  const displayAlerts = maxItems ? alerts.slice(0, maxItems) : alerts;

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'ERROR':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'WARNING':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return '🔴';
      case 'ERROR':
        return '🟠';
      case 'WARNING':
        return '🟡';
      default:
        return 'ℹ️';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `Hace ${diffMins} min`;
    } else if (diffHours < 24) {
      return `Hace ${diffHours}h`;
    } else if (diffDays < 7) {
      return `Hace ${diffDays}d`;
    } else {
      return date.toLocaleDateString('es-ES', {
        day: 'numeric',
        month: 'short',
      });
    }
  };

  if (displayAlerts.length === 0) {
    return (
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Alertas Recientes
        </h3>
        <div className="text-center py-8 text-gray-500">
          No hay alertas pendientes
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Alertas Recientes
      </h3>

      <div className="space-y-3">
        {displayAlerts.map((alert) => (
          <div
            key={alert.id}
            onClick={() => onAlertClick?.(alert)}
            className={`p-4 rounded-lg border transition-all ${
              alert.is_read ? 'bg-gray-50 border-gray-200' : 'bg-white border-gray-300'
            } ${onAlertClick ? 'hover:shadow-md cursor-pointer' : ''}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <span className="text-xl">{getSeverityIcon(alert.severity)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4
                      className={`text-sm font-medium ${
                        alert.is_read ? 'text-gray-700' : 'text-gray-900'
                      }`}
                    >
                      {alert.title}
                    </h4>
                    <span
                      className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full border ${getSeverityColor(
                        alert.severity
                      )}`}
                    >
                      {alert.severity_display}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                  <div className="flex items-center space-x-4 text-xs text-gray-500">
                    <span>{formatDate(alert.created_at)}</span>
                    {alert.asset_name && (
                      <span className="flex items-center">
                        📦 {alert.asset_name}
                      </span>
                    )}
                    {alert.is_resolved && (
                      <span className="text-green-600">✓ Resuelta</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Actions */}
              {!alert.is_resolved && (
                <div className="flex items-center space-x-2 ml-4">
                  {!alert.is_read && onMarkAsRead && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onMarkAsRead(alert.id);
                      }}
                      className="text-xs text-blue-600 hover:text-blue-800"
                      title="Marcar como leída"
                    >
                      ✓
                    </button>
                  )}
                  {onResolve && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onResolve(alert.id);
                      }}
                      className="text-xs text-green-600 hover:text-green-800"
                      title="Resolver"
                    >
                      ✓✓
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {maxItems && alerts.length > maxItems && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            Ver todas las alertas ({alerts.length})
          </button>
        </div>
      )}
    </div>
  );
};

export default AlertsList;
