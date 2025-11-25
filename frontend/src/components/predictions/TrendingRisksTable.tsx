/**
 * Trending Risks Table Component
 */
import React from 'react';

interface TrendingAsset {
  asset_id: string;
  asset_name: string;
  asset_code: string;
  current_probability: number;
  trend: number;
  trend_direction: 'increasing' | 'decreasing' | 'stable';
  prediction_count: number;
}

interface TrendingRisksTableProps {
  assets: TrendingAsset[];
  onAssetClick?: (assetId: string) => void;
}

const TrendingRisksTable: React.FC<TrendingRisksTableProps> = ({
  assets,
  onAssetClick,
}) => {
  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return <span className="text-red-600">↑</span>;
      case 'decreasing':
        return <span className="text-green-600">↓</span>;
      default:
        return <span className="text-gray-600">→</span>;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return 'text-red-600';
      case 'decreasing':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const getRiskBadgeColor = (probability: number) => {
    if (probability >= 75) return 'bg-red-100 text-red-800 border-red-200';
    if (probability >= 50) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (probability >= 25) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-green-100 text-green-800 border-green-200';
  };

  if (assets.length === 0) {
    return (
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Tendencias de Riesgo
        </h3>
        <div className="text-center py-8 text-gray-500">
          No hay suficientes datos para mostrar tendencias
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Tendencias de Riesgo (Últimos 30 días)
      </h3>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Activo
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Código
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Probabilidad Actual
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tendencia
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Predicciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {assets.map((asset) => (
              <tr
                key={asset.asset_id}
                onClick={() => onAssetClick?.(asset.asset_id)}
                className={onAssetClick ? 'hover:bg-gray-50 cursor-pointer' : ''}
              >
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {asset.asset_name}
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{asset.asset_code}</div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getRiskBadgeColor(
                      asset.current_probability
                    )}`}
                  >
                    {asset.current_probability.toFixed(1)}%
                  </span>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-center">
                  <div className="flex items-center justify-center space-x-1">
                    {getTrendIcon(asset.trend_direction)}
                    <span
                      className={`text-sm font-medium ${getTrendColor(
                        asset.trend_direction
                      )}`}
                    >
                      {asset.trend > 0 ? '+' : ''}
                      {asset.trend.toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-4 whitespace-nowrap text-center">
                  <span className="text-sm text-gray-600">
                    {asset.prediction_count}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TrendingRisksTable;
