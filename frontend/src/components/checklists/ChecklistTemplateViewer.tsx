/**
 * ChecklistTemplateViewer Component
 * Displays predefined checklist templates
 */
import React, { useEffect, useState } from 'react';
import { ChecklistTemplate, ChecklistItem } from '../../types/checklist.types';
import checklistService from '../../services/checklistService';

interface ChecklistTemplateViewerProps {
  templateId?: string;
  vehicleType?: string;
  onSelectTemplate?: (template: ChecklistTemplate) => void;
}

const ChecklistTemplateViewer: React.FC<ChecklistTemplateViewerProps> = ({
  templateId,
  vehicleType,
  onSelectTemplate,
}) => {
  const [templates, setTemplates] = useState<ChecklistTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] =
    useState<ChecklistTemplate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, [templateId, vehicleType]);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);

      if (templateId) {
        const template = await checklistService.getTemplate(templateId);
        setSelectedTemplate(template);
        setTemplates([template]);
      } else if (vehicleType) {
        const data = await checklistService.getTemplatesByVehicleType(
          vehicleType
        );
        setTemplates(data);
        if (data.length > 0) {
          setSelectedTemplate(data[0]);
        }
      } else {
        const data = await checklistService.getTemplates({
          is_system_template: true,
        });
        setTemplates(data.results);
        if (data.results.length > 0) {
          setSelectedTemplate(data.results[0]);
        }
      }
    } catch (err: any) {
      setError(err.message || 'Error cargando plantillas');
    } finally {
      setLoading(false);
    }
  };


  const handleSelectTemplate = (template: ChecklistTemplate) => {
    setSelectedTemplate(template);
    if (onSelectTemplate) {
      onSelectTemplate(template);
    }
  };

  const groupItemsBySection = (items: ChecklistItem[]) => {
    const grouped: { [key: string]: ChecklistItem[] } = {};
    items.forEach((item) => {
      if (!grouped[item.section]) {
        grouped[item.section] = [];
      }
      grouped[item.section].push(item);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={loadTemplates}
          className="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (!selectedTemplate) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-gray-600">No hay plantillas disponibles</p>
      </div>
    );
  }

  const groupedItems = groupItemsBySection(selectedTemplate.items);

  return (
    <div className="space-y-4">
      {/* Template Selector */}
      {templates.length > 1 && (
        <div className="bg-white rounded-lg shadow p-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar Plantilla
          </label>
          <select
            value={selectedTemplate.id}
            onChange={(e) => {
              const template = templates.find((t) => t.id === e.target.value);
              if (template) handleSelectTemplate(template);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.code} - {template.name}
              </option>
            ))}
          </select>
        </div>
      )}


      {/* Template Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {selectedTemplate.name}
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Código: {selectedTemplate.code}
              </p>
            </div>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              {selectedTemplate.vehicle_type_display}
            </span>
          </div>
          {selectedTemplate.description && (
            <p className="mt-4 text-gray-600">{selectedTemplate.description}</p>
          )}
          <div className="mt-4 flex gap-4 text-sm">
            <span className="text-gray-600">
              <strong>Items:</strong> {selectedTemplate.item_count}
            </span>
            <span className="text-gray-600">
              <strong>Puntaje Mínimo:</strong> {selectedTemplate.passing_score}
              %
            </span>
            <span className="text-gray-600">
              <strong>Completados:</strong> {selectedTemplate.response_count}
            </span>
          </div>
        </div>

        {/* Action Button */}
        {onSelectTemplate && (
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <button
              onClick={() => handleSelectTemplate(selectedTemplate)}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
              Iniciar Checklist con esta Plantilla
            </button>
          </div>
        )}

        {/* Checklist Items */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Items de Inspección
          </h3>
          <div className="space-y-6">
            {Object.entries(groupedItems).map(([section, items]) => (
              <div key={section}>
                <h4 className="text-md font-medium text-gray-800 mb-3 pb-2 border-b border-gray-200">
                  {section}
                </h4>
                <div className="space-y-2">
                  {items.map((item) => (
                    <div
                      key={item.order}
                      className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        {item.order}
                      </span>
                      <div className="flex-1">
                        <p className="text-gray-900">{item.question}</p>
                        <div className="mt-1 flex gap-2 text-xs text-gray-500">
                          {item.required && (
                            <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded">
                              Requerido
                            </span>
                          )}
                          {item.observations_allowed && (
                            <span className="px-2 py-0.5 bg-gray-200 text-gray-700 rounded">
                              Permite observaciones
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChecklistTemplateViewer;
