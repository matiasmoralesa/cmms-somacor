/**
 * Saved Filters Component
 * Permite guardar y cargar combinaciones de filtros
 */
import React, { useState, useEffect } from 'react';

interface SavedFilter {
  id: string;
  name: string;
  filters: Record<string, any>;
  createdAt: string;
}

interface SavedFiltersProps {
  storageKey: string;
  currentFilters: Record<string, any>;
  onLoadFilter: (filters: Record<string, any>) => void;
}

const SavedFilters: React.FC<SavedFiltersProps> = ({
  storageKey,
  currentFilters,
  onLoadFilter
}) => {
  const [savedFilters, setSavedFilters] = useState<SavedFilter[]>([]);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [filterName, setFilterName] = useState('');

  useEffect(() => {
    loadSavedFilters();
  }, [storageKey]);

  const loadSavedFilters = () => {
    const saved = localStorage.getItem(`${storageKey}_saved`);
    if (saved) {
      try {
        setSavedFilters(JSON.parse(saved));
      } catch (e) {
        console.error('Error loading saved filters:', e);
      }
    }
  };

  const saveCurrentFilters = () => {
    if (!filterName.trim()) return;

    const newFilter: SavedFilter = {
      id: Date.now().toString(),
      name: filterName.trim(),
      filters: currentFilters,
      createdAt: new Date().toISOString()
    };

    const updated = [...savedFilters, newFilter];
    setSavedFilters(updated);
    localStorage.setItem(`${storageKey}_saved`, JSON.stringify(updated));
    
    setFilterName('');
    setShowSaveModal(false);
  };

  const deleteFilter = (id: string) => {
    const updated = savedFilters.filter(f => f.id !== id);
    setSavedFilters(updated);
    localStorage.setItem(`${storageKey}_saved`, JSON.stringify(updated));
  };

  const hasActiveFilters = Object.values(currentFilters).some(
    v => v !== '' && v !== null && v !== undefined
  );

  if (savedFilters.length === 0 && !hasActiveFilters) {
    return null;
  }

  return (
    <div className="space-y-2">
      {/* Save Current Filters Button */}
      {hasActiveFilters && (
        <button
          onClick={() => setShowSaveModal(true)}
          className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          Guardar filtros actuales
        </button>
      )}

      {/* Saved Filters List */}
      {savedFilters.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Filtros guardados:</p>
          <div className="flex flex-wrap gap-2">
            {savedFilters.map(filter => (
              <div
                key={filter.id}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg group"
              >
                <button
                  onClick={() => onLoadFilter(filter.filters)}
                  className="text-sm text-gray-700 hover:text-gray-900 font-medium"
                >
                  {filter.name}
                </button>
                <button
                  onClick={() => deleteFilter(filter.id)}
                  className="text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Save Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Guardar Filtros</h3>
            <input
              type="text"
              value={filterName}
              onChange={(e) => setFilterName(e.target.value)}
              placeholder="Nombre para estos filtros"
              className="input mb-4"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && saveCurrentFilters()}
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowSaveModal(false);
                  setFilterName('');
                }}
                className="btn btn-secondary"
              >
                Cancelar
              </button>
              <button
                onClick={saveCurrentFilters}
                disabled={!filterName.trim()}
                className="btn btn-primary"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedFilters;
