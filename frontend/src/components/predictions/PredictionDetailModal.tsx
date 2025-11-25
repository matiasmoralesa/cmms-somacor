/**
 * Prediction Detail Modal Component
 */
import React from 'react';
import { FailurePrediction } from '../../types/prediction.types';

interface PredictionDetailModalProps {
  prediction: FailurePrediction | null;
  isOpen: boolean;
  onClose: () => void;
}

const PredictionDetailModal: React.FC<PredictionDetailModalProps> = ({
  prediction,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !prediction) return null;

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

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Detalle de Predicción
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                {prediction.asset_name} ({prediction.asset_code})
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Risk Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nivel de Riesgo
              </label>
              <span
                className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getRiskColor(
                  prediction.risk_level
                )}`}
              >
                {prediction.risk_level_display}
              </span>
            </div>

            {/* Probability */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Probabilidad de Falla
              </label>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-green-500 via-amber-500 to-red-500 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${prediction.failure_probability}%` }}
                    />
                  </div>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {prediction.failure_probability.toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Confidence Score */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confianza del Modelo
              </label>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-blue-500 h-4 rounded-full transition-all duration-500"
                      style={{ width: `${prediction.confidence_score}%` }}
                    />
                  </div>
                </div>
                <span className="text-2xl font-bold text-gray-900">
                  {prediction.confidence_score.toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Predicción
                </label>
                <p className="text-sm text-gray-900">
                  {new Date(prediction.prediction_date).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              </div>
              {prediction.predicted_failure_date && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha Predicha de Falla
                  </label>
                  <p className="text-sm text-gray-900">
                    {new Date(prediction.predicted_failure_date).toLocaleDateString(
                      'es-ES',
                      {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      }
                    )}
                  </p>
                </div>
              )}
            </div>

            {/* Model Info */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Versión del Modelo
              </label>
              <p className="text-sm text-gray-900">{prediction.model_version}</p>
            </div>

            {/* Recommendations */}
            {prediction.recommendations && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recomendaciones
                </label>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-gray-700 whitespace-pre-line">
                    {prediction.recommendations}
                  </p>
                </div>
              </div>
            )}

            {/* Input Features */}
            {prediction.input_features &&
              Object.keys(prediction.input_features).length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Características de Entrada
                  </label>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(prediction.input_features).map(
                        ([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key}:</span>
                            <span className="text-sm font-medium text-gray-900">
                              {typeof value === 'number'
                                ? value.toFixed(2)
                                : String(value)}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </div>
              )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
            <button onClick={onClose} className="btn btn-secondary">
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionDetailModal;
