/**
 * Asset Form Component
 * Form for creating and editing assets
 */
import React, { useState, useEffect } from 'react';
import type { Asset } from '../../types/asset.types';

interface AssetFormProps {
  asset?: Asset | null;
  onSubmit: (data: Partial<Asset>) => Promise<void>;
  onCancel: () => void;
}

const VEHICLE_TYPES = [
  { value: 'CAMION_SUPERSUCKER', label: 'Camión Supersucker' },
  { value: 'CAMIONETA_MDO', label: 'Camioneta MDO' },
  { value: 'RETROEXCAVADORA_MDO', label: 'Retroexcavadora MDO' },
  { value: 'CARGADOR_FRONTAL_MDO', label: 'Cargador Frontal MDO' },
  { value: 'MINICARGADOR_MDO', label: 'Minicargador MDO' },
];

const STATUS_OPTIONS = [
  { value: 'OPERATIONAL', label: 'Operacional' },
  { value: 'DOWN', label: 'Fuera de Servicio' },
  { value: 'MAINTENANCE', label: 'En Mantenimiento' },
  { value: 'RETIRED', label: 'Retirado' },
];

const AssetForm: React.FC<AssetFormProps> = ({ asset, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    asset_code: '',
    vehicle_type: '',
    serial_number: '',
    license_plate: '',
    manufacturer: '',
    model: '',
    installation_date: '',
    status: 'OPERATIONAL',
    location: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (asset) {
      setFormData({
        name: asset.name || '',
        asset_code: asset.asset_code || '',
        vehicle_type: asset.vehicle_type || '',
        serial_number: asset.serial_number || '',
        license_plate: asset.license_plate || '',
        manufacturer: asset.manufacturer || '',
        model: asset.model || '',
        installation_date: asset.installation_date || '',
        status: asset.status || 'OPERATIONAL',
        location: asset.location || '',
      });
    }
  }, [asset]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Error al guardar el equipo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: Camión 001"
          />
        </div>

        {/* Asset Code */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Código <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="asset_code"
            value={formData.asset_code}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: AST-001"
          />
        </div>

        {/* Vehicle Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Vehículo <span className="text-red-500">*</span>
          </label>
          <select
            name="vehicle_type"
            value={formData.vehicle_type}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Seleccionar tipo</option>
            {VEHICLE_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Serial Number */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Número de Serie <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="serial_number"
            value={formData.serial_number}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: SN123456"
          />
        </div>

        {/* License Plate */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Patente
          </label>
          <input
            type="text"
            name="license_plate"
            value={formData.license_plate}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: ABCD12"
          />
        </div>

        {/* Manufacturer */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fabricante
          </label>
          <input
            type="text"
            name="manufacturer"
            value={formData.manufacturer}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: Caterpillar"
          />
        </div>

        {/* Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Modelo
          </label>
          <input
            type="text"
            name="model"
            value={formData.model}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: 320D"
          />
        </div>

        {/* Installation Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Fecha de Instalación
          </label>
          <input
            type="date"
            name="installation_date"
            value={formData.installation_date}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estado <span className="text-red-500">*</span>
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {STATUS_OPTIONS.map(status => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Ubicación
          </label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: Bodega Principal"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
        >
          {loading && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          )}
          {asset ? 'Actualizar' : 'Crear'} Equipo
        </button>
      </div>
    </form>
  );
};

export default AssetForm;
