import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MachineStatusFormData } from '../../types/machineStatus.types';
import machineStatusService from '../../services/machineStatusService';
import { toast } from 'react-hot-toast';

const StatusUpdateForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState<any[]>([]);
  const [formData, setFormData] = useState<MachineStatusFormData>({
    asset: '',
    status_type: 'OPERANDO',
    odometer_reading: undefined,
    fuel_level: undefined,
    condition_notes: '',
    location: undefined,
  });

  useEffect(() => {
    fetchMyAssets();
  }, []);

  const fetchMyAssets = async () => {
    try {
      const data = await machineStatusService.getMyAssets();
      setAssets(data.assets || []);
    } catch (error) {
      console.error('Error fetching assets:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);
      await machineStatusService.create(formData);
      toast.success('Estado actualizado exitosamente');
      navigate('/machine-status');
    } catch (error: any) {
      console.error('Error updating status:', error);
      const errorMsg = error.response?.data?.asset?.[0] || 'Error al actualizar estado';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value || undefined,
    }));
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Actualizar Estado de Máquina</h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Asset Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Activo <span className="text-red-500">*</span>
            </label>
            <select
              name="asset"
              value={formData.asset}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Seleccionar activo</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} ({asset.asset_code})
                </option>
              ))}
            </select>
          </div>

          {/* Status Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estado <span className="text-red-500">*</span>
            </label>
            <select
              name="status_type"
              value={formData.status_type}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="OPERANDO">Operando</option>
              <option value="DETENIDA">Detenida</option>
              <option value="EN_MANTENIMIENTO">En Mantenimiento</option>
              <option value="FUERA_DE_SERVICIO">Fuera de Servicio</option>
            </select>
          </div>

          {/* Odometer Reading */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Lectura Odómetro/Horómetro
            </label>
            <input
              type="number"
              step="0.01"
              name="odometer_reading"
              value={formData.odometer_reading || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Ej: 12345.50"
            />
          </div>

          {/* Fuel Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nivel de Combustible (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              name="fuel_level"
              value={formData.fuel_level || ''}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="0-100"
            />
            {formData.fuel_level !== undefined && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div
                    className="bg-blue-600 h-2.5 rounded-full"
                    style={{ width: `${formData.fuel_level}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Condition Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notas de Condición
            </label>
            <textarea
              name="condition_notes"
              value={formData.condition_notes}
              onChange={handleChange}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Describe la condición actual del activo..."
            />
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate('/machine-status')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Guardando...' : 'Actualizar Estado'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StatusUpdateForm;
