/**
 * ChecklistViewer Component
 * Displays completed checklists
 */
import React, { useEffect, useState } from 'react';
import {
  ChecklistResponse,
  ChecklistResponseItem,
} from '../../types/checklist.types';
import checklistService from '../../services/checklistService';

interface ChecklistViewerProps {
  checklistId: string;
  onClose?: () => void;
}

const ChecklistViewer: React.FC<ChecklistViewerProps> = ({
  checklistId,
  onClose,
}) => {
  const [checklist, setChecklist] = useState<ChecklistResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    loadChecklist();
  }, [checklistId]);

  const loadChecklist = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await checklistService.getResponse(checklistId);
      setChecklist(data);
    } catch (err: any) {
      setError(err.message || 'Error cargando checklist');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!checklist) return;

    try {
      setDownloadingPdf(true);
      const { pdf_url } = await checklistService.getResponsePdf(checklist.id);
      checklistService.downloadPdf(pdf_url);
    } catch (err: any) {
      alert('Error descargando PDF: ' + err.message);
    } finally {
      setDownloadingPdf(false);
    }
  };

  const groupResponsesBySection = (responses: ChecklistResponseItem[]) => {
    // This would need template data to group properly
    // For now, return as is
    return { General: responses };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !checklist) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error || 'Checklist no encontrado'}</p>
        {onClose && (
          <button
            onClick={onClose}
            className="mt-2 text-red-600 hover:text-red-800 underline"
          >
            Cerrar
          </button>
        )}
      </div>
    );
  }


  const getResponseIcon = (response: string) => {
    switch (response) {
      case 'yes':
        return <span className="text-green-600 text-xl">✓</span>;
      case 'no':
        return <span className="text-red-600 text-xl">✗</span>;
      case 'na':
        return <span className="text-gray-600 text-xl">—</span>;
      default:
        return null;
    }
  };

  const getResponseText = (response: string) => {
    switch (response) {
      case 'yes':
        return 'Sí';
      case 'no':
        return 'No';
      case 'na':
        return 'N/A';
      default:
        return response;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {checklist.template_name}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Código: {checklist.template_code}
            </p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
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

        {/* Info Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Activo</p>
            <p className="font-medium text-gray-900">
              {checklist.asset_name} ({checklist.asset_code})
            </p>
          </div>
          <div>
            <p className="text-gray-500">Operador</p>
            <p className="font-medium text-gray-900">
              {checklist.operator_name}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Fecha</p>
            <p className="font-medium text-gray-900">
              {new Date(checklist.completed_at).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Completado por</p>
            <p className="font-medium text-gray-900">
              {checklist.completed_by_name}
            </p>
          </div>
        </div>

        {checklist.shift && (
          <div className="mt-4 text-sm">
            <span className="text-gray-500">Turno: </span>
            <span className="font-medium text-gray-900">{checklist.shift}</span>
          </div>
        )}

        {checklist.odometer_reading && (
          <div className="mt-2 text-sm">
            <span className="text-gray-500">Kilometraje/Horómetro: </span>
            <span className="font-medium text-gray-900">
              {checklist.odometer_reading}
            </span>
          </div>
        )}
      </div>


      {/* Score Section */}
      <div className="p-6 border-b border-gray-200">
        <div
          className={`rounded-lg p-4 ${
            checklist.passed
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}
        >
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Puntaje Obtenido</p>
              <p
                className={`text-3xl font-bold ${
                  checklist.passed ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {checklist.score}%
              </p>
            </div>
            <div className="text-right">
              <p
                className={`text-lg font-semibold ${
                  checklist.passed ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {checklist.passed ? '✓ APROBADO' : '✗ NO APROBADO'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Responses */}
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Respuestas
        </h3>
        <div className="space-y-3">
          {checklist.responses.map((response, index) => (
            <div
              key={index}
              className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg"
            >
              <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {response.item_order}
              </span>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  {getResponseIcon(response.response)}
                  <span className="font-medium text-gray-900">
                    {getResponseText(response.response)}
                  </span>
                </div>
                {response.notes && (
                  <p className="text-sm text-gray-600 mt-2">
                    <span className="font-medium">Observaciones:</span>{' '}
                    {response.notes}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Actions */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-3">
          {checklist.pdf_url && (
            <button
              onClick={handleDownloadPdf}
              disabled={downloadingPdf}
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              {downloadingPdf ? 'Descargando...' : 'Descargar PDF'}
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="py-2 px-4 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
            >
              Cerrar
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChecklistViewer;
