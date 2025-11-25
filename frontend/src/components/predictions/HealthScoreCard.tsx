/**
 * Health Score Card Component
 */
import React from 'react';
import { AssetHealthScore } from '../../types/prediction.types';

interface HealthScoreCardProps {
  asset: AssetHealthScore;
  onClick?: () => void;
}

const HealthScoreCard: React.FC<HealthScoreCardProps> = ({ asset, onClick }) => {
  const getHealthColor = (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'amber';
    if (score >= 40) return 'orange';
    return 'red';
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const healthColor = getHealthColor(asset.health_score);
  const riskColorClass = getRiskColor(asset.risk_level);

  return (
    <div
      onClick={onClick}
      className={`card p-6 ${onClick ? 'card-hover cursor-pointer' : ''}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">
            {asset.asset_name}
          </h3>
          <p className="text-sm text-gray-500">{asset.asset_code}</p>
        </div>
        <span className={`badge border ${riskColorClass}`}>
          {asset.risk_level_display}
        </span>
      </div>

      {/* Health Score Circle */}
      <div className="flex items-center justify-center mb-4">
        <div className="relative w-32 h-32">
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-200"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${(asset.health_score / 100) * 351.86} 351.86`}
              className={`text-${healthColor}-600 transition-all duration-500`}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold text-${healthColor}-600`}>
              {Math.round(asset.health_score)}
            </span>
            <span className="text-xs text-gray-500">Health Score</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Probabilidad de Falla:</span>
          <span className="font-medium text-gray-900">
            {asset.failure_probability.toFixed(1)}%
          </span>
        </div>
        {asset.predicted_failure_date && (
          <div className="flex justify-between">
            <span className="text-gray-600">Fecha Predicha:</span>
            <span className="font-medium text-gray-900">
              {new Date(asset.predicted_failure_date).toLocaleDateString('es-ES', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
              })}
            </span>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-gray-600">Última Predicción:</span>
          <span className="font-medium text-gray-900">
            {new Date(asset.last_prediction).toLocaleDateString('es-ES', {
              day: 'numeric',
              month: 'short',
            })}
          </span>
        </div>
      </div>
    </div>
  );
};

export default HealthScoreCard;
