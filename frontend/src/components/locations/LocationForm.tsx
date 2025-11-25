import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LocationFormData } from '../../types/location.types';
import locationService from '../../services/locationService';
import { toast } from 'react-hot-toast';

const LocationForm = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<LocationFormData>({
    name: '',
    address: '',
    city: '',
    region: '',
    coordinates: undefined,
    description: '',
    is_active: true,
  });

  useEffect(() => {
    if (isEdit && id) {
      fetchLocation(id);
    }
  }, [id, isEdit]);

  const fetchLocation = async (locationId: string) => {
    try {
      setLoading(true);
      const data = await locationService.getById(locationId);
      setFormData({
        name: data.name,
        address: data.address || '',
        city: data.city || '',
        region: data.region || '',
        coordinates: data.coordinates,
        description: data.description || '',
        is_active: data.is_active,
      });
    } catch (error) {
      console.error('Error fetching location:', error);
      toast.error('Error al cargar ubicación');
      navigate('/locations');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);
      if (isEdit && id) {
        await locationService.update(id, formData);
        toast.success('Ubicación actualizada exitosamente');
      } else {
        await locationService.create(formData);
        toast.success('Ubicación creada exitosamente');
      }
      navigate('/locations');
    } catch (error: any) {
      console.error('Error saving location:', error);
      const errorMsg = error.response?.data?.name?.[0] || 'Error al guardar ubicación';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleCoordinatesChange = (field: 'lat' | 'lng', value: string) => {
    const numValue = value === '' ? undefined : parseFloat(value);
    setFormData((prev) => ({
      ...prev,
      coordinates: {
        lat: field === 'lat' ? (numValue || 0) : (prev.coordinates?.lat || 0),
        lng: field === 'lng' ? (numValue || 0) : (prev.coordinates?.lng || 0),
      },
    }));
  };

  if (loading && isEdit) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {isEdit ? 'Editar Ubicación' : 'Nueva Ubicación'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Nombre <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Planta Santiago"
            />
          </div>

          {/* Address */}
          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
              Dirección
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Av. Libertador 1234"
            />
          </div>

          {/* City and Region */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">
                Ciudad
              </label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ej: Santiago"
              />
            </div>
            <div>
              <label htmlFor="region" className="block text-sm font-medium text-gray-700 mb-1">
                Región
              </label>
              <input
                type="text"
                id="region"
                name="region"
                value={formData.region}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Ej: Región Metropolitana"
              />
            </div>
          </div>

          {/* Coordinates */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Coordenadas (Opcional)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <input
                  type="number"
                  step="any"
                  value={formData.coordinates?.lat || ''}
                  onChange={(e) => handleCoordinatesChange('lat', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Latitud (ej: -33.4489)"
                />
              </div>
              <div>
                <input
                  type="number"
                  step="any"
                  value={formData.coordinates?.lng || ''}
                  onChange={(e) => handleCoordinatesChange('lng', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Longitud (ej: -70.6693)"
                />
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
              Descripción
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Descripción adicional de la ubicación"
            />
          </div>

          {/* Active Status */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
              Ubicación activa
            </label>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => navigate('/locations')}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Guardando...' : isEdit ? 'Actualizar' : 'Crear'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LocationForm;
