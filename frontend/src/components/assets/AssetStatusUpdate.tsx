/**
 * Asset Status Update Component
 * Allows operators to update machine status
 */
import { useState } from 'react';
import { AlertCircle, CheckCircle, Wrench, XCircle } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'react-hot-toast';

interface AssetStatusUpdateProps {
  assetId: string;
  currentStatus: string;
  assetName: string;
  onStatusUpdated?: () => void;
}

const STATUS_OPTIONS = [
  { value: 'OPERATIONAL', label: 'Operativo', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
  { value: 'DOWN', label: 'Fuera de Servicio', icon: XCircle, color: 'text-red-600', bg: 'bg-red-50' },
  { value: 'MAINTENANCE', label: 'En Mantenimiento', icon: Wrench, color: 'text-yellow-600', bg: 'bg-yellow-50' },
  { value: 'RETIRED', label: 'Retirado', icon: AlertCircle, color: 'text-gray-600', bg: 'bg-gray-50' },
];

export default function AssetStatusUpdate({ assetId, currentStatus, assetName, onStatusUpdated }: AssetStatusUpdateProps) {
  const [selectedStatus, setSelectedStatus] = useState(currentStatus);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedStatus === currentStatus) {
      toast.error('Selecciona un estado diferente');
      return;
    }

    setLoading(true);
    
    try {
      await api.patch(`/assets/${assetId}/update-status/`, {
        status: selectedStatus,
        notes: notes
      });
      
      toast.success('Estado actualizado correctamente');
      setNotes('');
      
      if (onStatusUpdated) {
        onStatusUpdated();
      }
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Error al actualizar estado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4">Actualizar Estado de Máquina</h3>
      <p className="text-gray-600 mb-4">{assetName}</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Status Options */}
        <div className="grid grid-cols-2 gap-3">
          {STATUS_OPTIONS.map((option) => {
            const Icon = option.icon;
            const isSelected = selectedStatus === option.value;
            const isCurrent = currentStatus === option.value;
            
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setSelectedStatus(option.value)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } ${isCurrent ? 'ring-2 ring-green-500' : ''}`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${option.bg}`}>
                    <Icon className={option.color} size={20} />
                  </div>
                  <div className="text-left">
                    <div className="font-medium text-sm">{option.label}</div>
                    {isCurrent && (
                      <div className="text-xs text-green-600">Estado actual</div>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notas (opcional)
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Describe el motivo del cambio de estado..."
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || selectedStatus === currentStatus}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? 'Actualizando...' : 'Actualizar Estado'}
        </button>
      </form>
    </div>
  );
}
