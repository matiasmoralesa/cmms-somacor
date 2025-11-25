/**
 * useWorkOrderFilters Hook
 * 
 * Custom hook for managing work order filters including asset status.
 */

import { useState, useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

export interface WorkOrderFilters {
  status?: string;
  priority?: string;
  work_order_type?: string;
  assigned_to?: string;
  asset?: string;
  has_asset?: boolean | null;
  search?: string;
}

export function useWorkOrderFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  // Parse filters from URL
  const filters = useMemo<WorkOrderFilters>(() => {
    const params: WorkOrderFilters = {};
    
    if (searchParams.has('status')) {
      params.status = searchParams.get('status') || undefined;
    }
    if (searchParams.has('priority')) {
      params.priority = searchParams.get('priority') || undefined;
    }
    if (searchParams.has('work_order_type')) {
      params.work_order_type = searchParams.get('work_order_type') || undefined;
    }
    if (searchParams.has('assigned_to')) {
      params.assigned_to = searchParams.get('assigned_to') || undefined;
    }
    if (searchParams.has('asset')) {
      params.asset = searchParams.get('asset') || undefined;
    }
    if (searchParams.has('has_asset')) {
      const value = searchParams.get('has_asset');
      params.has_asset = value === 'true' ? true : value === 'false' ? false : null;
    }
    if (searchParams.has('search')) {
      params.search = searchParams.get('search') || undefined;
    }
    
    return params;
  }, [searchParams]);
  
  // Update filters
  const updateFilters = useCallback((newFilters: Partial<WorkOrderFilters>) => {
    const params = new URLSearchParams(searchParams);
    
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        params.delete(key);
      } else {
        params.set(key, String(value));
      }
    });
    
    setSearchParams(params);
  }, [searchParams, setSearchParams]);
  
  // Clear all filters
  const clearFilters = useCallback(() => {
    setSearchParams(new URLSearchParams());
  }, [setSearchParams]);
  
  // Toggle has_asset filter
  const toggleAssetFilter = useCallback(() => {
    const currentValue = filters.has_asset;
    let newValue: boolean | null = null;
    
    if (currentValue === null || currentValue === undefined) {
      newValue = true; // Show only with asset
    } else if (currentValue === true) {
      newValue = false; // Show only without asset
    } else {
      newValue = null; // Show all
    }
    
    updateFilters({ has_asset: newValue });
  }, [filters.has_asset, updateFilters]);
  
  // Get filter count
  const filterCount = useMemo(() => {
    return Object.keys(filters).length;
  }, [filters]);
  
  // Check if any filters are active
  const hasActiveFilters = filterCount > 0;
  
  return {
    filters,
    updateFilters,
    clearFilters,
    toggleAssetFilter,
    filterCount,
    hasActiveFilters,
  };
}

export default useWorkOrderFilters;
