/**
 * Priority Manager Component
 */
import React, { useState, useEffect } from 'react';
import {
  getPriorities,
  createPriority,
  updatePriority,
  deletePriority,
  Priority
} from '../../services/configService';

const PriorityManager: React.FC = () => {
  const [priorities, setPriorities] = useState<Priority[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingPriority, setEditingPriority] = useState<Priority | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    level: '',
    color: '#808080',
    response_time_hours: '',
    is_active: true
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPriorities();
  }, []);

  const loadPriorities = async () => {
    try {
      setLoading(true);
      const data = await getPriorities();
      setPriorities(data.results || data);
    } catch (err) {
      setError('Error al cargar prioridades');
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
        level: parseInt(formData.level),
        response_time_hours: formData.response_time_hours ? parseInt(formData.response_time_hours) : null
      };

      if (editingPriority) {
        await updatePriority(editingPriority.id, payload);
      } else {
        await createPriority(payload);
      }
      await loadPriorities();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al guardar prioridad');
    }
  };

  const handleEdit = (priority: Priority) => {
    setEditingPriority(priority);
    setFormData({
      name: priority.name,
      code: priority.code,
      description: priority.description,
      level: priority.level.toString(),
      color: priority.color,
      response_time_hours: priority.response_time_hours?.toString() || '',
      is_active: priority.is_active
    });
    setShowModal(true);
  };

  const handleDelete = async (priority: Priority) => {
    if (priority.is_system) {
      alert('No se pueden eliminar prioridades del sistema');
      return;
    }

    if (!confirm(`¿Eliminar la prioridad "${priority.name}"?`)) return;

    try {
      await deletePriority(priority.id);
      await loadPriorities();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error al eliminar prioridad');
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPriority(null);
    setFormData({
      name: '',
      code: '',
      description: '',
      level: '',
      color: '#808080',
      response_time_hours: '',
      is_active: true
    });
    setError(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Prioridades</h2>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          + Nueva Prioridad
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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nivel</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Color</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Tiempo Respuesta</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Estado</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {priorities.map((priority) => (
                <tr key={priority.id}>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {priority.level}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                    {priority.name}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">{priority.code}</td>
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    <div className="flex items-center justify-center">
                      <div
                        className="w-6 h-6 rounded border border-gray-300"
                        style={{ backgroundColor: priority.color }}
                      />
                    </div>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center text-sm text-gray-600">
                    {priority.response_time_hours ? `${priority.response_time_hours}h` : '-'}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      priority.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {priority.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-center text-sm">
                    <button onClick={() => handleEdit(priority)} className="text-blue-600 hover:text-blue-900 mr-3">
                      Editar
                    </button>
                    {!priority.is_system && (
                      <button onClick={() => handleDelete(priority)} className="text-red-600 hover:text-red-900">
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
              {editingPriority ? 'Editar Prioridad' : 'Nueva Prioridad'}
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nivel * (1=más alto)</label>
                  <input
                    type="number"
                    value={formData.level}
                    onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                    className="input"
                    min="1"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                  <input
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    className="input h-10"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tiempo de Respuesta (horas)
                  </label>
                  <input
                    type="number"
                    value={formData.response_time_hours}
                    onChange={(e) => setFormData({ ...formData, response_time_hours: e.target.value })}
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
                  {editingPriority ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PriorityManager;
