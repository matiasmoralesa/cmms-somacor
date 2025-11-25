/**
 * Advanced Filters Component
 * Componente reutilizable para filtros avanzados con persistencia en URL
 */
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export interface FilterField {
  name: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'daterange' | 'multiselect' | 'number';
  options?: { value: string; label: string }[];
  placeholder?: string;
}

interface AdvancedFiltersProps {
  fields: FilterField[];
  onFilterChange: (filters: Record<string, any>) => void;
  onReset?: () => void;
}

const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({
  fields,
  onFilterChange,
  onReset
}) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<Record<string, any>>({});
  const [showFilters, setShowFilters] = useState(false);

  // Cargar filtros desde URL al montar
  useEffect(() => {
    const initialFilters: Record<string, any> = {};
    fields.forEach(field => {
      const value = searchParams.get(field.name);
      if (value) {
        initialFilters[field.name] = value;
      }
    });
    setFilters(initialFilters);
    if (Object.keys(initialFilters).length > 0) {
      setShowFilters(true);
    }
  }, []);

  // Actualizar URL cuando cambian los filtros
  useEffect(() => {
    const params = new URLSearchParams(searchParams);
    
    // Limpiar parámetros de filtros existentes
    fields.forEach(field => {
      params.delete(field.name);
    });

    // Agregar filtros activos
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        params.set(key, String(value));
      }
    });

    setSearchParams(params, { replace: true });
    onFilterChange(filters);
  }, [filters]);

  const handleFilterChange = (name: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleReset = () => {
    setFilters({});
    if (onReset) {
      onReset();
    }
  };

  const activeFiltersCount = Object.values(filters).filter(v => v !== '' && v !== null && v !== undefined).length;

  const renderField = (field: FilterField) => {
    const value = filters[field.name] || '';

    switch (field.type) {
      case 'text':
      case 'number':
        return (
          <input
            type={field.type}
            value={value}
            onChange={(e) => handleFilterChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className="input"
          />
        );

      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleFilterChange(field.name, e.target.value)}
            className="input"
          >
            <option value="">Todos</option>
            {field.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'date':
        return (
          <input
            type="date"
            value={value}
            onChange={(e) => handleFilterChange(field.name, e.target.value)}
            className="input"
          />
        );

      case 'daterange':
        return (
          <div className="grid grid-cols-2 gap-2">
            <input
              type="date"
              value={filters[`${field.name}_start`] || ''}
              onChange={(e) => handleFilterChange(`${field.name}_start`, e.target.value)}
              placeholder="Desde"
              className="input"
            />
            <input
              type="date"
              value={filters[`${field.name}_end`] || ''}
              onChange={(e) => handleFilterChange(`${field.name}_end`, e.target.value)}
              placeholder="Hasta"
              className="input"
            />
          </div>
        );

      case 'multiselect':
        const selectedValues = value ? value.split(',') : [];
        return (
          <div className="space-y-2">
            {field.options?.map(option => (
              <label key={option.value} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(option.value)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...selectedValues, option.value]
                      : selectedValues.filter(v => v !== option.value);
                    handleFilterChange(field.name, newValues.join(','));
                  }}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Toggle Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span className="font-medium">Filtros</span>
          {activeFiltersCount > 0 && (
            <span className="px-2 py-0.5 text-xs font-semibold text-white bg-blue-600 rounded-full">
              {activeFiltersCount}
            </span>
          )}
          <svg
            className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {activeFiltersCount > 0 && (
          <button
            onClick={handleReset}
            className="text-sm text-gray-600 hover:text-gray-900 underline"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {fields.map(field => (
              <div key={field.name}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {field.label}
                </label>
                {renderField(field)}
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Limpiar
            </button>
            <button
              onClick={() => setShowFilters(false)}
              className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      )}

      {/* Active Filters Tags */}
      {activeFiltersCount > 0 && !showFilters && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(filters).map(([key, value]) => {
            if (!value) return null;
            const field = fields.find(f => f.name === key);
            if (!field) return null;

            let displayValue = value;
            if (field.type === 'select') {
              const option = field.options?.find(o => o.value === value);
              displayValue = option?.label || value;
            }

            return (
              <div
                key={key}
                className="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
              >
                <span className="font-medium">{field.label}:</span>
                <span>{displayValue}</span>
                <button
                  onClick={() => handleFilterChange(key, '')}
                  className="hover:text-blue-900"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default AdvancedFilters;
