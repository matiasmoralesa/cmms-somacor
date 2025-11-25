/**
 * System Parameter Manager Component
 */
import React, { useState, useEffect } from 'react';
import {
  getSystemParameters,
  createSystemParameter,
  updateSystemParameter,
  deleteSystemParameter,
  SystemParameter
} from '../../services/configService';

const SystemParameterManager: React.FC = () => {
  const [parameters, setParameters] = useState<SystemParameter[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingParameter, setEditingParameter] = useState<SystemParameter | null>(null);
  const [formData, setFormData] = useState({
    key: '',
    value: '',
    data_type: 'STRING' as 'STRING' | 'INTEGER' | 'FLOAT' | 'BOOLEAN' | 'JSON',
    description: '',
    is_sensitive: false
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadParameters();
  }, []);

  const loadParameters = async () => {
    try {
      setLoading(true);
      const data = await getSystemParameters();
      setParameters(data.results || data);
    } catch (err) {
      setError('Error al cargar parámetros');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      if (editingParameter) {
        await updateSystemParameter(editingParameter.id, formData);
      } else {
        await createSystemParameter(formData);
      }
      await loadParameters();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al guardar parámetro');
    }
  };

  const handleEdit = (parameter: SystemParameter) => {
    setEditingParameter(parameter);
    setFormData({
      key: parameter.key,
      value: parameter.value,
      data_type: parameter.data_type,
      description: parameter.description,
      is_sensitive: parameter.is_sensitive
    });
    setShowModal(true);
  };

  const handleDelete = async (parameter: SystemParameter) => {
    if (!confirm(`¿Eliminar el parámetro "${parameter.key}"?`)) return;

    try {
      await deleteSystemParameter(parameter.id);
      await loadParameters();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Error al eliminar parámetro');
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingParameter(null);
    setFormData({
      key: '',
      value: '',
      data_type: 'STRING',
      description: '',
      is_sensitive: false
    });
    setError(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Parámetros del Sistema</h2>
        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          + Nuevo Parámetro
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
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Clave</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {parameters.map((param) => (
                <tr key={param.id}>
                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {param.key}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {param.is_sensitive ? '••••••••' : param.value}
                  </td>
                  <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      {param.data_type}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">{param.description}</td>
                  <td className="px-4 py-4 whitespace-nowrap text-center text-sm">
                    <button onClick={() => handleEdit(param)} className="text-blue-600 hover:text-blue-900 mr-3">
                      Editar
                    </button>
                    <button onClick={() => handleDelete(param)} className="text-red-600 hover:text-red-900">
                      Eliminar
                    </button>
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
              {editingParameter ? 'Editar Parámetro' : 'Nuevo Parámetro'}
            </h3>

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-800 rounded">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Clave *</label>
                  <input
                    type="text"
                    value={formData.key}
                    onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                    className="input"
                    required
                    disabled={!!editingParameter}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Dato *</label>
                  <select
                    value={formData.data_type}
                    onChange={(e) => setFormData({ ...formData, data_type: e.target.value as any })}
                    className="input"
                    required
                  >
                    <option value="STRING">String</option>
                    <option value="INTEGER">Integer</option>
                    <option value="FLOAT">Float</option>
                    <option value="BOOLEAN">Boolean</option>
                    <option value="JSON">JSON</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Valor *</label>
                  {formData.data_type === 'BOOLEAN' ? (
                    <select
                      value={formData.value}
                      onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                      className="input"
                      required
                    >
                      <option value="">Seleccionar...</option>
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                  ) : formData.data_type === 'JSON' ? (
                    <textarea
                      value={formData.value}
                      onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                      className="input font-mono text-sm"
                      rows={5}
                      required
                      placeholder='{"key": "value"}'
                    />
                  ) : (
                    <input
                      type={formData.data_type === 'INTEGER' || formData.data_type === 'FLOAT' ? 'number' : 'text'}
                      step={formData.data_type === 'FLOAT' ? 'any' : undefined}
                      value={formData.value}
                      onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                      className="input"
                      required
                    />
                  )}
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
                    id="is_sensitive"
                    checked={formData.is_sensitive}
                    onChange={(e) => setFormData({ ...formData, is_sensitive: e.target.checked })}
                    className="mr-2"
                  />
                  <label htmlFor="is_sensitive" className="text-sm text-gray-700">
                    Valor Sensible (ocultar en UI)
                  </label>
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button type="button" onClick={handleCloseModal} className="btn btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingParameter ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemParameterManager;
