/**
 * Maintenance Plan Form Component
 */
import React, { useState, useEffect } from 'react';
import type { MaintenancePlan } from '../../types/maintenance.types';
import assetService from '../../services/assetService';
import type { Asset } from '../../types/asset.types';

interface MaintenancePlanFormProps {
  plan?: MaintenancePlan | null;
  onSubmit: (data: Partial<MaintenancePlan>) => Promise<void>;
  onCancel: () => void;
}

const PLAN_TYPES = [
  { value: 'PREVENTIVE', label: 'Preventivo' },
  { value: 'PREDICTIVE', label: 'Predictivo' },
];

const RECURRENCE_TYPES = [
  { value: 'DAILY', label: 'Diario' },
  { value: 'WEEKLY', label: 'Semanal' },
  { value: 'MONTHLY', label: 'Mensual' },
  { value: 'CUSTOM', label: 'Personalizado' },
];

const MaintenancePlanForm: React.FC<MaintenancePlanFormProps> = ({ plan, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    asset: '',
    plan_type: 'PREVENTIVE',
    recurrence_type: 'MONTHLY',
    recurrence_interval: '1',
    next_due_date: '',
    is_active: true,
    estimated_duration: '',
  });
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingAssets, setLoadingAssets] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAssets();
  }, []);

  useEffect(() => {
    if (plan) {
      setFormData({
        name: plan.name || '',
        asset: plan.asset || '',
        plan_type: plan.plan_type || 'PREVENTIVE',
        recurrence_type: plan.recurrence_type || 'MONTHLY',
        recurrence_interval: plan.recurrence_interval?.toString() || '1',
        next_due_date: plan.next_due_date ? plan.next_due_date.split('T')[0] : '',
        is_active: plan.is_active !== undefined ? plan.is_active : true,
        estimated_duration: plan.estimated_duration?.toString() || '',
      });
    }
  }, [plan]);

  const loadAssets = async () => {
    try {
      const data = await assetService.getAssets();
      setAssets(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error loading assets:', err);
    } finally {
      setLoadingAssets(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const submitData: any = {
        ...formData,
        recurrence_interval: parseInt(formData.recurrence_interval),
        estimated_duration: parseInt(formData.estimated_duration),
      };

      await onSubmit(submitData);
    } catch (err: any) {
      setError(err.response?.data?.message || err.message || 'Error al guardar el plan de mantenimiento');
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
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Plan <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: Mantenimiento Mensual Motor"
          />
        </div>

        {/* Asset */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Equipo <span className="text-red-500">*</span>
          </label>
          {loadingAssets ? (
            <div className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
              Cargando equipos...
            </div>
          ) : (
            <select
              name="asset"
              value={formData.asset}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Seleccionar equipo</option>
              {assets.map(asset => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} ({asset.asset_code})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Plan Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tipo de Plan <span className="text-red-500">*</span>
          </label>
          <select
            name="plan_type"
            value={formData.plan_type}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {PLAN_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Recurrence Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Frecuencia <span className="text-red-500">*</span>
          </label>
          <select
            name="recurrence_type"
            value={formData.recurrence_type}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {RECURRENCE_TYPES.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Recurrence Interval */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Intervalo <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="recurrence_interval"
            value={formData.recurrence_interval}
            onChange={handleChange}
            required
            min="1"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: 1"
          />
          <p className="mt-1 text-xs text-gray-500">
            Cada cuántos períodos se ejecuta (ej: cada 2 semanas)
          </p>
        </div>

        {/* Next Due Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Próxima Fecha <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="next_due_date"
            value={formData.next_due_date}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Estimated Duration */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Duración Estimada (minutos) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="estimated_duration"
            value={formData.estimated_duration}
            onChange={handleChange}
            required
            min="1"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Ej: 120"
          />
        </div>

        {/* Is Active */}
        <div className="md:col-span-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm font-medium text-gray-700">
              Plan activo
            </span>
          </label>
          <p className="mt-1 text-xs text-gray-500 ml-6">
            Los planes activos generarán órdenes de trabajo automáticamente
          </p>
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
          {plan ? 'Actualizar' : 'Crear'} Plan
        </button>
      </div>
    </form>
  );
};

export default MaintenancePlanForm;
