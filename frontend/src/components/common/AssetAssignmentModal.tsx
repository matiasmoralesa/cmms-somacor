/**
 * AssetAssignmentModal Component
 * 
 * Modal for assigning an asset to a work order that doesn't have one.
 */

import React, { useState, useEffect } from 'react';
import Modal from './Modal';
import type { WorkOrder } from '../../types/workOrder.types';

interface Asset {
  id: string;
  name: string;
  asset_code: string;
  vehicle_type: string;
  status: string;
}

interface AssetAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  workOrder: WorkOrder;
  onAssign: (assetId: string) => Promise<void>;
}

export const AssetAssignmentModal: React.FC<AssetAssignmentModalProps> = ({
  isOpen,
  onClose,
  workOrder,
  onAssign,
}) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load assets when modal opens
  useEffect(() => {
    if (isOpen) {
      loadAssets();
    }
  }, [isOpen]);

  const loadAssets = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // TODO: Replace with actual API call
      // const response = await assetService.getAssets({ status: 'OPERATIONAL' });
      // setAssets(response);
      
      // Mock data for now
      setAssets([
        {
          id: '1',
          name: 'Excavadora CAT 320',
          asset_code: 'EXC-001',
          vehicle_type: 'RETROEXCAVADORA_MDO',
          status: 'OPERATIONAL',
        },
        {
          id: '2',
          name: 'Camión Supersucker',
          asset_code: 'CAM-001',
          vehicle_type: 'CAMION_SUPERSUCKER',
          status: 'OPERATIONAL',
        },
      ]);
    } catch (err) {
      setError('Error al cargar los equipos');
      console.error('Error loading assets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedAssetId) {
      setError('Debe seleccionar un equipo');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await onAssign(selectedAssetId);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error al asignar el equipo');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredAssets = assets.filter(
    (asset) =>
      asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      asset.asset_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Modal open={isOpen} onOpenChange={(open) => !open && onClose()} title="Asignar Equipo">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Work Order Info */}
        <div className="bg-gray-50 p-3 rounded-md">
          <p className="text-sm text-gray-600">Orden de Trabajo</p>
          <p className="font-medium">{workOrder.work_order_number}</p>
          <p className="text-sm text-gray-700">{workOrder.title}</p>
        </div>

        {/* Search */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Buscar Equipo
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar por nombre o código..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Asset List */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar Equipo *
          </label>
          
          {loading ? (
            <div className="text-center py-4">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="text-sm text-gray-600 mt-2">Cargando equipos...</p>
            </div>
          ) : filteredAssets.length === 0 ? (
            <p className="text-sm text-gray-500 py-4 text-center">
              No se encontraron equipos disponibles
            </p>
          ) : (
            <div className="max-h-64 overflow-y-auto border border-gray-300 rounded-md">
              {filteredAssets.map((asset) => (
                <label
                  key={asset.id}
                  className={`flex items-center p-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0 ${
                    selectedAssetId === asset.id ? 'bg-blue-50' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name="asset"
                    value={asset.id}
                    checked={selectedAssetId === asset.id}
                    onChange={(e) => setSelectedAssetId(e.target.value)}
                    className="mr-3"
                  />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{asset.name}</p>
                    <p className="text-sm text-gray-600">
                      Código: {asset.asset_code} | Tipo: {asset.vehicle_type}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={submitting || !selectedAssetId}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Asignando...' : 'Asignar Equipo'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default AssetAssignmentModal;
