/**
 * AssetDisplay Component
 * 
 * Displays asset information with proper null handling.
 * Shows a placeholder when no asset is assigned.
 */

import React from 'react';
import type { WorkOrder } from '../../types/workOrder.types';
import { hasAsset, formatAssetInfo } from '../../utils/workOrderHelpers';

interface AssetDisplayProps {
  workOrder: WorkOrder;
  showIcon?: boolean;
  className?: string;
  onAssignClick?: () => void;
}

export const AssetDisplay: React.FC<AssetDisplayProps> = ({
  workOrder,
  showIcon = true,
  className = '',
  onAssignClick,
}) => {
  if (!hasAsset(workOrder)) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        {showIcon && (
          <svg
            className="w-5 h-5 text-yellow-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        )}
        <span className="text-gray-500 italic">Sin equipo asignado</span>
        {onAssignClick && (
          <button
            onClick={onAssignClick}
            className="text-blue-600 hover:text-blue-800 text-sm underline"
          >
            Asignar
          </button>
        )}
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {showIcon && (
        <svg
          className="w-5 h-5 text-gray-600"
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
      )}
      <span className="text-gray-900">{formatAssetInfo(workOrder)}</span>
    </div>
  );
};

export default AssetDisplay;
