/**
 * ChecklistExecutor Component
 * Mobile-optimized interface for completing checklists
 */
import React, { useState, useEffect } from 'react';
import {
  ChecklistTemplate,
  ChecklistResponseItem,
  ChecklistResponseCreate,
} from '../../types/checklist.types';
import checklistService from '../../services/checklistService';

interface ChecklistExecutorProps {
  template: ChecklistTemplate;
  assetId: string;
  assetName: string;
  workOrderId?: string;
  onComplete?: (responseId: string) => void;
  onCancel?: () => void;
}

const ChecklistExecutor: React.FC<ChecklistExecutorProps> = ({
  template,
  assetId,
  assetName,
  workOrderId,
  onComplete,
  onCancel,
}) => {
  const [responses, setResponses] = useState<ChecklistResponseItem[]>([]);
  const [operatorName, setOperatorName] = useState('');
  const [shift, setShift] = useState('');
  const [odometerReading, setOdometerReading] = useState<number | undefined>();
  const [signatureUrl, setSignatureUrl] = useState<string | undefined>();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(false);

  useEffect(() => {
    // Initialize responses array
    const initialResponses: ChecklistResponseItem[] = template.items.map(
      (item) => ({
        item_order: item.order,
        response: 'na' as 'yes' | 'no' | 'na',
        notes: '',
      })
    );
    setResponses(initialResponses);
  }, [template]);

  const handleResponseChange = (
    itemIndex: number,
    response: 'yes' | 'no' | 'na',
    notes?: string
  ) => {
    const updatedResponses = [...responses];
    updatedResponses[itemIndex] = {
      ...updatedResponses[itemIndex],
      response,
      notes: notes !== undefined ? notes : updatedResponses[itemIndex].notes,
    };
    setResponses(updatedResponses);
  };


  const handleSubmit = async () => {
    if (!operatorName.trim()) {
      setError('El nombre del operador es requerido');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const data: ChecklistResponseCreate = {
        template: template.id,
        asset: assetId,
        work_order: workOrderId,
        responses,
        operator_name: operatorName,
        shift: shift || undefined,
        odometer_reading: odometerReading,
        signature_url: signatureUrl,
      };

      const response = await checklistService.completeChecklist(data);

      if (onComplete) {
        onComplete(response.id);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error al completar checklist');
    } finally {
      setSubmitting(false);
    }
  };

  const calculateScore = () => {
    const yesCount = responses.filter((r) => r.response === 'yes').length;
    return Math.round((yesCount / responses.length) * 100);
  };

  const groupItemsBySection = (items: typeof template.items) => {
    const grouped: { [key: string]: typeof template.items } = {};
    items.forEach((item) => {
      if (!grouped[item.section]) {
        grouped[item.section] = [];
      }
      grouped[item.section].push(item);
    });
    return grouped;
  };

  const calculateProgress = () => {
    const answered = responses.filter((r) => r.response !== 'na').length;
    return Math.round((answered / responses.length) * 100);
  };

  // Don't render until responses are initialized
  if (responses.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const groupedItems = groupItemsBySection(template.items);

  if (showSummary) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-lg font-bold text-gray-900">
                Información Final
              </h1>
              <button
                onClick={() => setShowSummary(false)}
                className="text-gray-600 hover:text-gray-900"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Summary Content */}
        <div className="flex-1 max-w-4xl mx-auto w-full px-4 py-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Operador *
                </label>
                <input
                  type="text"
                  value={operatorName}
                  onChange={(e) => setOperatorName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ingrese su nombre"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Turno
                </label>
                <select
                  value={shift}
                  onChange={(e) => setShift(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Seleccionar turno</option>
                  <option value="Mañana">Mañana</option>
                  <option value="Tarde">Tarde</option>
                  <option value="Noche">Noche</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kilometraje / Horómetro
                </label>
                <input
                  type="number"
                  value={odometerReading || ''}
                  onChange={(e) =>
                    setOdometerReading(
                      e.target.value ? parseInt(e.target.value) : undefined
                    )
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ingrese lectura"
                />
              </div>
            </div>

            {/* Score Preview */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-gray-700 font-medium">
                  Puntaje Estimado:
                </span>
                <span className="text-2xl font-bold text-blue-600">
                  {calculateScore()}%
                </span>
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Puntaje mínimo requerido: {template.passing_score}%
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-white border-t border-gray-200 sticky bottom-0">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <button
              onClick={handleSubmit}
              disabled={submitting || !operatorName.trim()}
              className="w-full py-3 px-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Enviando...' : 'Completar Checklist'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-2">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {template.name}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {assetName} • Código: {template.code}
              </p>
            </div>
            {onCancel && (
              <button
                onClick={onCancel}
                className="text-gray-600 hover:text-gray-900 p-2"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
          {/* Progress Bar */}
          <div className="mt-3">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Progreso: {calculateProgress()}%</span>
              <span>
                {responses.filter((r) => r.response !== 'na').length} de{' '}
                {template.items.length} respondidas
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${calculateProgress()}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="space-y-6">
          {Object.entries(groupedItems).map(([section, items]) => (
            <div key={section} className="bg-white rounded-lg shadow">
              {/* Section Header */}
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  {section}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  {items.length} items
                </p>
              </div>

              {/* Section Items */}
              <div className="p-6 space-y-4">
                {items.map((item, itemIndex) => {
                  const responseIndex = template.items.findIndex(
                    (i) => i.order === item.order
                  );
                  const response = responses[responseIndex];

                  return (
                    <div
                      key={item.order}
                      className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                    >
                      {/* Question */}
                      <div className="flex items-start gap-3 mb-3">
                        <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                          {item.order}
                        </span>
                        <div className="flex-1">
                          <p className="text-gray-900 font-medium">
                            {item.question}
                          </p>
                          {item.required && (
                            <span className="inline-block mt-1 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded">
                              Requerido
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Response Buttons */}
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        <button
                          onClick={() =>
                            handleResponseChange(responseIndex, 'yes')
                          }
                          className={`py-2 px-3 rounded-lg font-medium text-sm transition-all ${
                            response?.response === 'yes'
                              ? 'bg-green-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          ✓ Sí
                        </button>
                        <button
                          onClick={() =>
                            handleResponseChange(responseIndex, 'no')
                          }
                          className={`py-2 px-3 rounded-lg font-medium text-sm transition-all ${
                            response?.response === 'no'
                              ? 'bg-red-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          ✗ No
                        </button>
                        <button
                          onClick={() =>
                            handleResponseChange(responseIndex, 'na')
                          }
                          className={`py-2 px-3 rounded-lg font-medium text-sm transition-all ${
                            response?.response === 'na'
                              ? 'bg-gray-600 text-white shadow-md'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          — N/A
                        </button>
                      </div>

                      {/* Notes */}
                      {item.observations_allowed && (
                        <div>
                          <textarea
                            value={response?.notes || ''}
                            onChange={(e) =>
                              handleResponseChange(
                                responseIndex,
                                response?.response || 'na',
                                e.target.value
                              )
                            }
                            rows={2}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="Observaciones (opcional)..."
                          />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 sticky bottom-0 shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex gap-3">
            {onCancel && (
              <button
                onClick={onCancel}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200"
              >
                Cancelar
              </button>
            )}
            <button
              onClick={() => setShowSummary(true)}
              className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
            >
              Continuar a Información Final →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChecklistExecutor;
