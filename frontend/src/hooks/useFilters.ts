/**
 * Custom Hook for Filter Management
 * Maneja filtros con persistencia en localStorage y URL
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

interface UseFiltersOptions {
  storageKey?: string;
  defaultFilters?: Record<string, any>;
}

export const useFilters = (options: UseFiltersOptions = {}) => {
  const { storageKey, defaultFilters = {} } = options;
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState<Record<string, any>>(defaultFilters);

  // Cargar filtros guardados al montar
  useEffect(() => {
    // Primero intentar cargar desde URL
    const urlFilters: Record<string, any> = {};
    searchParams.forEach((value, key) => {
      urlFilters[key] = value;
    });

    // Si no hay filtros en URL, intentar cargar desde localStorage
    if (Object.keys(urlFilters).length === 0 && storageKey) {
      const savedFilters = localStorage.getItem(storageKey);
      if (savedFilters) {
        try {
          const parsed = JSON.parse(savedFilters);
          setFilters({ ...defaultFilters, ...parsed });
          return;
        } catch (e) {
          console.error('Error parsing saved filters:', e);
        }
      }
    }

    if (Object.keys(urlFilters).length > 0) {
      setFilters({ ...defaultFilters, ...urlFilters });
    }
  }, []);

  // Actualizar URL y localStorage cuando cambian los filtros
  useEffect(() => {
    // Actualizar URL
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        params.set(key, String(value));
      }
    });
    setSearchParams(params, { replace: true });

    // Guardar en localStorage
    if (storageKey) {
      localStorage.setItem(storageKey, JSON.stringify(filters));
    }
  }, [filters, storageKey]);

  const updateFilter = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const updateFilters = (newFilters: Record<string, any>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters
    }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
    if (storageKey) {
      localStorage.removeItem(storageKey);
    }
  };

  const clearFilter = (key: string) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[key];
      return newFilters;
    });
  };

  const hasActiveFilters = () => {
    return Object.values(filters).some(v => v !== '' && v !== null && v !== undefined);
  };

  const getActiveFiltersCount = () => {
    return Object.values(filters).filter(v => v !== '' && v !== null && v !== undefined).length;
  };

  return {
    filters,
    updateFilter,
    updateFilters,
    resetFilters,
    clearFilter,
    hasActiveFilters: hasActiveFilters(),
    activeFiltersCount: getActiveFiltersCount()
  };
};

export default useFilters;
