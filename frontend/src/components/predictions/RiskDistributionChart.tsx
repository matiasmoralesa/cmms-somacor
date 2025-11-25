/**
 * Risk Distribution Chart Component
 */
import React from 'react';

interface RiskDistributionChartProps {
  distribution: Record<string, number>;
}

const RiskDistributionChart: React.FC<RiskDistributionChartProps> = ({
  distribution,
}) => {
  const riskLevels = [
    { key: 'LOW', label: 'Bajo', color: 'bg-green-500' },
    { key: 'MEDIUM', label: 'Medio', color: 'bg-amber-500' },
    { key: 'HIGH', label: 'Alto', color: 'bg-orange-500' },
    { key: 'CRITICAL', label: 'Crítico', color: 'bg-red-500' },
  ];

  const total = Object.values(distribution).reduce((sum, val) => sum + val, 0);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Distribución de Riesgo
      </h3>

      {/* Bar Chart */}
      <div className="space-y-4 mb-6">
        {riskLevels.map((level) => {
          const count = distribution[level.key] || 0;
          const percentage = total > 0 ? (count / total) * 100 : 0;

          return (
            <div key={level.key}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">
                  {level.label}
                </span>
                <span className="text-sm text-gray-600">
                  {count} ({percentage.toFixed(0)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`${level.color} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            Total de Activos
          </span>
          <span className="text-lg font-semibold text-gray-900">{total}</span>
        </div>
      </div>
    </div>
  );
};

export default RiskDistributionChart;
