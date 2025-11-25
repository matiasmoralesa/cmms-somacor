/**
 * Work Order Type Manager Component
 */
import React, { useState, useEffect } from 'react';
import {
  getWorkOrderTypes,
  createWorkOrderType,
  updateWorkOrderType,
  deleteWorkOrderType,
  WorkOrderType,
  getPriorities,
  Priority
} from '../../services/configService';

const WorkOrderTypeManager: React.FC = () => {
  const [types, setTypes] = useState<WorkOrderType[]>([]);
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingType, setEditingType] = useState<WorkOrderType | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    requires_approval: false,
    default_priority: '',
    estimated_hours: '',
    is_active: true
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [typesData, prioritiesData] = await Promise.all([
        getWorkOrderTypes(),
        getPriorities()
      ]);
      setTypes(typesData.results || typesData);
      setPriorities(prioritiesData.results || prioritiesData);
    } catch (err) {
      setError('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const payload = {
        ...formData,
        default_priority: formData.default_priority || null,
        estimated_hours: formData.estimated_hours ? parseFloat(formData.estimated_hours) : null
      };

      if (editingType) {
        await updateWorkOrderType(editingType.id, payload);
      } else {
        await createWorkOrderType(payload);
      }
      await loadData();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al guardar tipo de OT');
    }
  };

  const handleEdit = (type: WorkOrderType) => {
    setEditingType(type);
    setFormData({
      name: type.name,
      code: type.code,
      description: type.description,
      requires_approval: type.requires_approval,
      default_priority: type.default_priority || '',
      estimated_hours: type.estimated_hours?.toString() || '',
      is_active: type.is_active
    });
    setShowModal(true);
  };

  const handleDelete = async (type: WorkOrderType) => {
    if (type.is_system) {
      alert('No se pueden eliminar tipos del sistema');
      return;
    }

    if (!confirm(`¿Eliminar el tipo "${type.name}"?`)) return;

    try {
      await deleteWorkOrderType(type.id);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error al eliminar tipo');
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingType(null);
    setFormData({
      name: '',
      code: '',
      description: '',
      requires_approval: false,
      default_priority: '',
      estimated_hours: '',
      is_active: true
    });
    setError(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Tipos de Órdenes de Trabajo</h2>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          + Nuevo Tipo
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Requiere Aprobación</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Horas Estimadas</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {types.map((type) => (
                <tr key={type.id}>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {type.name}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">{type.code}</td>
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    {type.requires_approval ? '✓' : '-'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-600">
                    {type.estimated_hours || '-'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      type.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {type.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center text-sm">
                    <button onClick={() => handleEdit(type)} className="text-blue-600 hover:text-blue-900 mr-3">
                      Editar
                    </button>
                    {!type.is_system && (
                      <button onClick={() => handleDelete(type)} className="text-red-600 hover:text-red-900">
                        Eliminar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">
              {editingType ? 'Editar Tipo de OT' : 'Nuevo Tipo de OT'}
            </h3>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Código *</label>
                  <input
                    type="text"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    className="input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Prioridad por Defecto</label>
                  <select
                    value={formData.default_priority}
                    onChange={(e) => setFormData({ ...formData, default_priority: e.target.value })}
                    className="input"
                  >
                    <option value="">Sin prioridad por defecto</option>
                    {priorities.map((priority) => (
                      <option key={priority.id} value={priority.id}>{priority.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Horas Estimadas</label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.estimated_hours}
                    onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                    className="input"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="input"
                    rows={3}
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="requires_approval"
                    checked={formData.requires_approval}
                    onChange={(e) => setFormData({ ...formData, requires_approval: e.target.checked })}
                    className="mr-2"
                  />
                  <label htmlFor="requires_approval" className="text-sm text-gray-700">
                    Requiere Aprobación
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="mr-2"
                  />
                  <label htmlFor="is_active" className="text-sm text-gray-700">Activo</label>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={handleCloseModal} className="btn btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingType ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkOrderTypeManager;
