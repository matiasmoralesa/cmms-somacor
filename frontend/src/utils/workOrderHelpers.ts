/**
 * Work Order Helper Functions
 * 
 * Utility functions for safely accessing and displaying work order data,
 * particularly handling cases where asset information may be null or undefined.
 */

import type { WorkOrder } from '../types/workOrder.types';

/**
 * Check if a work order has an asset assigned
 * 
 * @param workOrder - The work order to check
 * @returns true if the work order has an asset assigned, false otherwise
 * 
 * @example
 * ```typescript
 * if (hasAsset(workOrder)) {
 *   console.log('Asset:', workOrder.asset_name);
 * }
 * ```
 */
export function hasAsset(workOrder: WorkOrder): boolean {
  return workOrder.asset !== null && workOrder.asset !== undefined && workOrder.asset !== '';
}

/**
 * Safely get the asset display name
 * 
 * Returns the asset name if available, otherwise returns a placeholder message.
 * 
 * @param workOrder - The work order containing asset information
 * @returns The asset name or "Sin equipo asignado" if no asset
 * 
 * @example
 * ```typescript
 * const displayName = getAssetDisplayName(workOrder);
 * // Returns: "Excavadora CAT 320" or "Sin equipo asignado"
 * ```
 */
export function getAssetDisplayName(workOrder: WorkOrder): string {
  if (!workOrder.asset_name) {
    return 'Sin equipo asignado';
  }
  return workOrder.asset_name;
}

/**
 * Safely get the asset code
 * 
 * Returns the asset code if available, otherwise returns "N/A".
 * 
 * @param workOrder - The work order containing asset information
 * @returns The asset code or "N/A" if not available
 * 
 * @example
 * ```typescript
 * const code = getAssetCode(workOrder);
 * // Returns: "EXC-001" or "N/A"
 * ```
 */
export function getAssetCode(workOrder: WorkOrder): string {
  return workOrder.asset_code || 'N/A';
}

/**
 * Format asset information for display
 * 
 * Combines asset name and code into a formatted string suitable for display.
 * Handles cases where asset information is missing or incomplete.
 * 
 * @param workOrder - The work order containing asset information
 * @returns Formatted asset information string
 * 
 * @example
 * ```typescript
 * formatAssetInfo(workOrder);
 * // Returns: "Excavadora CAT 320 (EXC-001)"
 * // Or: "Sin equipo asignado" if no asset
 * // Or: "Excavadora CAT 320" if no code
 * ```
 */
export function formatAssetInfo(workOrder: WorkOrder): string {
  if (!hasAsset(workOrder)) {
    return 'Sin equipo asignado';
  }
  
  const parts: string[] = [];
  
  if (workOrder.asset_name) {
    parts.push(workOrder.asset_name);
  }
  
  if (workOrder.asset_code) {
    parts.push(`(${workOrder.asset_code})`);
  }
  
  return parts.length > 0 ? parts.join(' ') : 'Equipo sin nombre';
}

/**
 * Get a short asset identifier
 * 
 * Returns the asset code if available, otherwise returns the asset name,
 * or a placeholder if neither is available.
 * 
 * @param workOrder - The work order containing asset information
 * @returns Short asset identifier
 * 
 * @example
 * ```typescript
 * getAssetShortId(workOrder);
 * // Returns: "EXC-001" (prefers code)
 * // Or: "Excavadora" (falls back to name)
 * // Or: "Sin equipo" (if nothing available)
 * ```
 */
export function getAssetShortId(workOrder: WorkOrder): string {
  if (!hasAsset(workOrder)) {
    return 'Sin equipo';
  }
  
  return workOrder.asset_code || workOrder.asset_name || 'Sin identificador';
}

/**
 * Check if asset information is complete
 * 
 * Determines if the work order has complete asset information
 * (both name and code are present).
 * 
 * @param workOrder - The work order to check
 * @returns true if asset information is complete, false otherwise
 */
export function hasCompleteAssetInfo(workOrder: WorkOrder): boolean {
  return !!(workOrder.asset && workOrder.asset_name && workOrder.asset_code);
}

/**
 * Get asset display with fallback
 * 
 * Returns formatted asset info, or a custom fallback message if no asset.
 * 
 * @param workOrder - The work order containing asset information
 * @param fallback - Custom fallback message (default: "Sin equipo asignado")
 * @returns Formatted asset information or fallback message
 * 
 * @example
 * ```typescript
 * getAssetDisplayWithFallback(workOrder, 'No asignado');
 * // Returns: "Excavadora (EXC-001)" or "No asignado"
 * ```
 */
export function getAssetDisplayWithFallback(
  workOrder: WorkOrder,
  fallback: string = 'Sin equipo asignado'
): string {
  if (!hasAsset(workOrder)) {
    return fallback;
  }
  
  return formatAssetInfo(workOrder);
}
