/**
 * AssetSelector Component
 * Allows selecting an asset compatible with a checklist template
 */
import React, { useEffect, useState } from 'react';
import assetService, { Asset } from '../../services/assetService';
import { ChecklistTemplate } from '../../types/checklist.types';

interface AssetSelectorProps {
  template: ChecklistTemplate;
  onSelectAsset: (asset: Asset) => void;
  onCancel: () => void;
}

const AssetSelector: React.FC<AssetSelectorProps> = ({
  template,
  onSelectAsset,
  onCancel,
}) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  useEffect(() => {
    loadCompatibleAssets();
  }, [template]);

  const loadCompatibleAssets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get assets that match the template's vehicle type
      const data = await assetService.getAssets({
        vehicle_type: template.vehicle_type
      });
      
      // Filter only operational assets
      const operationalAssets = data.filter(
        (asset) => asset.status === 'OPERATIONAL'
      );
      
      setAssets(operationalAssets);
    } catch (err: any) {
      setError(err.message || 'Error cargando activos');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAsset = (asset: Asset) => {
    setSelectedAsset(asset);
  };

  const handleConfirm = () => {
    if (selectedAsset) {
      onSelectAsset(selectedAsset);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Seleccionar Activo
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Plantilla: {template.name}
                </p>
                <p className="text-sm text-gray-500">
                  Tipo requerido: {template.vehicle_type_display}
                </p>
              </div>
              <button
                onClick={onCancel}
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
          </div>

          {/* Content */}
          <div className="p-6">
            {error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800">{error}</p>
                <button
                  onClick={loadCompatibleAssets}
                  className="mt-2 text-red-600 hover:text-red-800 underline"
                >
                  Reintentar
                </button>
              </div>
            ) : assets.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  No hay activos disponibles
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  No se encontraron activos operativos del tipo{' '}
                  {template.vehicle_type_display}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {assets.map((asset) => (
                  <button
                    key={asset.id}
                    onClick={() => handleSelectAsset(asset)}
                    className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                      selectedAsset?.id === asset.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">
                          {asset.name}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Código: {asset.asset_code}
                        </p>
                        <div className="mt-2 flex flex-wrap gap-2 text-sm">
                          <span className="text-gray-600">
                            {asset.manufacturer} {asset.model}
                          </span>
                          {asset.license_plate && (
                            <span className="text-gray-600">
                              • Patente: {asset.license_plate}
                            </span>
                          )}
                          <span className="text-gray-600">
                            • Serie: {asset.serial_number}
                          </span>
                        </div>
                      </div>
                      {selectedAsset?.id === asset.id && (
                        <div className="ml-4">
                          <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                            <svg
                              className="w-4 h-4 text-white"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          </div>
                        </div>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200 bg-gray-50">
            <div className="flex gap-3">
              <button
                onClick={onCancel}
                className="flex-1 py-3 px-4 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                disabled={!selectedAsset}
                className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continuar con este Activo
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetSelector;
