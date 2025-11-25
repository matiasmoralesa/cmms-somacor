/**
 * Checklists Page
 * Main page for checklist management
 */
import React, { useState, useEffect } from 'react';
import { ChecklistResponse, ChecklistTemplate } from '../types/checklist.types';
import { Asset } from '../services/assetService';
import checklistService from '../services/checklistService';
import ChecklistTemplateViewer from '../components/checklists/ChecklistTemplateViewer';
import ChecklistExecutor from '../components/checklists/ChecklistExecutor';
import ChecklistViewer from '../components/checklists/ChecklistViewer';
import AssetSelector from '../components/checklists/AssetSelector';
import Toast from '../components/common/Toast';
import { useToast } from '../hooks/useToast';

type ViewMode = 'list' | 'templates' | 'selectAsset' | 'execute' | 'view';

const Checklists: React.FC = () => {
  const { toast, success, error: showError, closeToast } = useToast();
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [checklists, setChecklists] = useState<ChecklistResponse[]>([]);
  const [selectedTemplate, setSelectedTemplate] =
    useState<ChecklistTemplate | null>(null);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [selectedChecklistId, setSelectedChecklistId] = useState<string | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterPassed, setFilterPassed] = useState<boolean | undefined>();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (viewMode === 'list') {
      loadChecklists();
    }
  }, [viewMode, filterPassed, searchTerm]);

  const loadChecklists = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await checklistService.getResponses({
        passed: filterPassed,
        search: searchTerm || undefined,
        ordering: '-completed_at',
      });
      setChecklists(data.results);
    } catch (err: any) {
      setError(err.message || 'Error cargando checklists');
    } finally {
      setLoading(false);
    }
  };

  const handleStartChecklist = (template: ChecklistTemplate) => {
    setSelectedTemplate(template);
    setViewMode('selectAsset');
  };

  const handleAssetSelected = (asset: Asset) => {
    setSelectedAsset(asset);
    setViewMode('execute');
  };

  const handleChecklistComplete = (checklistId: string) => {
    success('Checklist Completado', 'El checklist fue completado exitosamente');
    setSelectedChecklistId(checklistId);
    setViewMode('view');
    loadChecklists();
  };

  const handleViewChecklist = (checklistId: string) => {
    setSelectedChecklistId(checklistId);
    setViewMode('view');
  };

  const handleBackToList = () => {
    setViewMode('list');
    setSelectedTemplate(null);
    setSelectedAsset(null);
    setSelectedChecklistId(null);
  };


  // Render based on view mode
  if (viewMode === 'templates') {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-6">
            <button
              onClick={handleBackToList}
              className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
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
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Volver
            </button>
          </div>
          <ChecklistTemplateViewer onSelectTemplate={handleStartChecklist} />
        </div>
      </div>
    );
  }

  if (viewMode === 'selectAsset' && selectedTemplate) {
    return (
      <AssetSelector
        template={selectedTemplate}
        onSelectAsset={handleAssetSelected}
        onCancel={handleBackToList}
      />
    );
  }

  if (viewMode === 'execute' && selectedTemplate && selectedAsset) {
    return (
      <ChecklistExecutor
        template={selectedTemplate}
        assetId={selectedAsset.id}
        assetName={selectedAsset.name}
        onComplete={handleChecklistComplete}
        onCancel={handleBackToList}
      />
    );
  }

  if (viewMode === 'view' && selectedChecklistId) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <ChecklistViewer
            checklistId={selectedChecklistId}
            onClose={handleBackToList}
          />
        </div>
      </div>
    );
  }

  // Default: List view
  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <Toast
        open={toast.open}
        onOpenChange={closeToast}
        title={toast.title}
        description={toast.description}
        type={toast.type}
      />
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Checklists</h1>
          <p className="text-gray-600">
            Gestiona y completa checklists de inspección
          </p>
        </div>

        {/* Actions */}
        <div className="mb-6 flex gap-3">
          <button
            onClick={() => setViewMode('templates')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 flex items-center gap-2"
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
                d="M12 4v16m8-8H4"
              />
            </svg>
            Nuevo Checklist
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por operador..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Estado
              </label>
              <select
                value={
                  filterPassed === undefined
                    ? 'all'
                    : filterPassed
                    ? 'passed'
                    : 'failed'
                }
                onChange={(e) => {
                  const value = e.target.value;
                  setFilterPassed(
                    value === 'all'
                      ? undefined
                      : value === 'passed'
                      ? true
                      : false
                  );
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos</option>
                <option value="passed">Aprobados</option>
                <option value="failed">No Aprobados</option>
              </select>
            </div>
          </div>
        </div>


        {/* Checklist List */}
        {loading ? (
          <div className="flex justify-center items-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            <button
              onClick={loadChecklists}
              className="mt-2 text-red-600 hover:text-red-800 underline"
            >
              Reintentar
            </button>
          </div>
        ) : checklists.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              No hay checklists
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Comienza creando un nuevo checklist
            </p>
            <div className="mt-6">
              <button
                onClick={() => setViewMode('templates')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
              >
                Nuevo Checklist
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {checklists.map((checklist) => (
              <div
                key={checklist.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleViewChecklist(checklist.id)}
              >
                <div className="p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {checklist.template_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {checklist.template_code}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        checklist.passed
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {checklist.score}%
                    </span>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                        />
                      </svg>
                      <span>{checklist.asset_name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                      <span>{checklist.operator_name}</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                        />
                      </svg>
                      <span>
                        {new Date(checklist.completed_at).toLocaleDateString(
                          'es-ES',
                          {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                          }
                        )}
                      </span>
                    </div>
                  </div>

                  {checklist.pdf_url && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          checklistService
                            .getResponsePdf(checklist.id)
                            .then(({ pdf_url }) =>
                              checklistService.downloadPdf(pdf_url)
                            );
                        }}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-1"
                      >
                        <svg
                          className="w-4 h-4"
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
                        Descargar PDF
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Checklists;
