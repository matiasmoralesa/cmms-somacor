/**
 * Inventory Page - Complete CRUD for Spare Parts
 */
import React, { useState, useEffect } from 'react';
import inventoryService from '../services/inventoryService';
import SparePartForm from '../components/inventory/SparePartForm';
import type { SparePart } from '../types/inventory.types';

const InventoryPage: React.FC = () => {
  const [spareParts, setSpareParts] = useState<SparePart[]>([]);
  const [filteredParts, setFilteredParts] = useState<SparePart[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedPart, setSelectedPart] = useState<SparePart | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [stockFilter, setStockFilter] = useState<string>('ALL');
  const [adjustQuantity, setAdjustQuantity] = useState('');
  const [adjustType, setAdjustType] = useState('IN');
  const [adjustNotes, setAdjustNotes] = useState('');

  useEffect(() => {
    loadSpareParts();
  }, []);

  useEffect(() => {
    filterParts();
  }, [spareParts, searchTerm, categoryFilter, stockFilter]);

  const loadSpareParts = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading spare parts...');
      const data = await inventoryService.getSpareParts();
      console.log('Spare parts loaded:', data);
      setSpareParts(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error loading spare parts:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });
      setError(err.response?.data?.message || err.message || 'Error al cargar el inventario');
      setSpareParts([]);
    } finally {
      setLoading(false);
    }
  };

  const filterParts = () => {
    let filtered = [...spareParts];

    if (categoryFilter !== 'ALL') {
      filtered = filtered.filter(part => part.category === categoryFilter);
    }

    if (stockFilter === 'LOW') {
      filtered = filtered.filter(part => part.quantity <= part.minimum_stock);
    } else if (stockFilter === 'OUT') {
      filtered = filtered.filter(part => part.quantity === 0);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(part =>
        part.name.toLowerCase().includes(term) ||
        part.part_number.toLowerCase().includes(term) ||
        part.category?.toLowerCase().includes(term)
      );
    }

    setFilteredParts(filtered);
  };

  const handleCreate = async (data: Partial<SparePart>) => {
    await inventoryService.createSparePart(data);
    closeModals();
    loadSpareParts();
  };

  const handleUpdate = async (data: Partial<SparePart>) => {
    if (selectedPart) {
      await inventoryService.updateSparePart(selectedPart.id, data);
      closeModals();
      loadSpareParts();
    }
  };

  const handleDelete = async () => {
    if (selectedPart) {
      try {
        await inventoryService.deleteSparePart(selectedPart.id);
        closeModals();
        loadSpareParts();
      } catch (err: any) {
        alert(err.response?.data?.message || 'Error al eliminar el repuesto');
      }
    }
  };

  const handleAdjustStock = async () => {
    if (selectedPart && adjustQuantity) {
      try {
        await inventoryService.adjustStock(
          selectedPart.id,
          parseInt(adjustQuantity),
          adjustType,
          adjustNotes
        );
        closeModals();
        loadSpareParts();
      } catch (err: any) {
        alert(err.response?.data?.message || 'Error al ajustar el stock');
      }
    }
  };

  const handleRowClick = (part: SparePart) => {
    setSelectedPart(part);
    setShowDetailModal(true);
  };

  const handleEdit = (part: SparePart) => {
    setSelectedPart(part);
    setShowEditModal(true);
  };

  const handleDeleteClick = (part: SparePart) => {
    setSelectedPart(part);
    setShowDeleteModal(true);
  };

  const handleAdjustClick = (part: SparePart) => {
    setSelectedPart(part);
    setAdjustQuantity('');
    setAdjustType('IN');
    setAdjustNotes('');
    setShowAdjustModal(true);
  };

  const closeModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDetailModal(false);
    setShowDeleteModal(false);
    setShowAdjustModal(false);
    setSelectedPart(null);
  };

  const categories = Array.from(new Set(spareParts.map(p => p.category))).filter(Boolean);
  const lowStockCount = spareParts.filter(p => p.quantity <= p.minimum_stock).length;
  const totalValue = spareParts.reduce((sum, p) => sum + (p.quantity * p.unit_cost), 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Cargando inventario...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <svg className="w-6 h-6 text-red-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <button onClick={loadSpareParts} className="mt-3 text-sm font-medium text-red-800 hover:text-red-900 underline">
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventario de Repuestos</h1>
          <p className="text-gray-600 mt-1">Control de repuestos, materiales y alertas de stock</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          + Agregar Repuesto
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por nombre, número o categoría..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Categoría</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ALL">Todas las categorías</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Stock</label>
            <select
              value={stockFilter}
              onChange={(e) => setStockFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="ALL">Todos</option>
              <option value="LOW">Stock Bajo</option>
              <option value="OUT">Sin Stock</option>
            </select>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Items</p>
          <p className="text-2xl font-bold text-gray-900">{spareParts.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Stock Bajo</p>
          <p className="text-2xl font-bold text-red-600">{lowStockCount}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Valor Total</p>
          <p className="text-2xl font-bold text-green-600">${totalValue.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Categorías</p>
          <p className="text-2xl font-bold text-blue-600">{categories.length}</p>
        </div>
      </div>

      {lowStockCount > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-yellow-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Alerta de Stock Bajo</h3>
              <p className="mt-1 text-sm text-yellow-700">
                Hay {lowStockCount} repuesto(s) con stock bajo o agotado
              </p>
            </div>
          </div>
        </div>
      )}

      {filteredParts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {searchTerm || categoryFilter !== 'ALL' || stockFilter !== 'ALL' ? 'No se encontraron repuestos' : 'No hay repuestos registrados'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm || categoryFilter !== 'ALL' || stockFilter !== 'ALL' ? 'Intenta ajustar los filtros' : 'Comienza agregando repuestos al inventario'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-700">
              Mostrando <span className="font-medium">{filteredParts.length}</span> de <span className="font-medium">{spareParts.length}</span> repuestos
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Número</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ubicación</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Costo Unit.</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredParts.map((part) => (
                  <tr key={part.id} onClick={() => handleRowClick(part)} className="hover:bg-gray-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{part.part_number}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{part.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{part.category}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        part.quantity === 0 ? 'bg-red-100 text-red-800' :
                        part.quantity <= part.minimum_stock ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {part.quantity} / {part.minimum_stock}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{part.location}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${part.unit_cost.toFixed(2)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button onClick={(e) => { e.stopPropagation(); handleAdjustClick(part); }} className="text-green-600 hover:text-green-900">
                        Ajustar
                      </button>
                      <button onClick={(e) => { e.stopPropagation(); handleEdit(part); }} className="text-blue-600 hover:text-blue-900">
                        Editar
                      </button>
                      <button onClick={(e) => { e.stopPropagation(); handleDeleteClick(part); }} className="text-red-600 hover:text-red-900">
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Nuevo Repuesto</h2>
                <button onClick={closeModals} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <SparePartForm onSubmit={handleCreate} onCancel={closeModals} />
            </div>
          </div>
        </div>
      )}

      {showEditModal && selectedPart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Editar Repuesto</h2>
                <button onClick={closeModals} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <SparePartForm sparePart={selectedPart} onSubmit={handleUpdate} onCancel={closeModals} />
            </div>
          </div>
        </div>
      )}

      {showAdjustModal && selectedPart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Ajustar Stock</h3>
            <p className="text-sm text-gray-600 mb-4">
              <strong>{selectedPart.name}</strong><br />
              Stock actual: {selectedPart.quantity}
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Movimiento</label>
                <select
                  value={adjustType}
                  onChange={(e) => setAdjustType(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="IN">Entrada (+)</option>
                  <option value="OUT">Salida (-)</option>
                  <option value="ADJUSTMENT">Ajuste</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Cantidad</label>
                <input
                  type="number"
                  value={adjustQuantity}
                  onChange={(e) => setAdjustQuantity(e.target.value)}
                  min="1"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Cantidad"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Notas</label>
                <textarea
                  value={adjustNotes}
                  onChange={(e) => setAdjustNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Motivo del ajuste..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t">
                <button onClick={closeModals} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                  Cancelar
                </button>
                <button onClick={handleAdjustStock} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Ajustar Stock
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDetailModal && selectedPart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">{selectedPart.name}</h2>
                  <p className="text-sm text-gray-500 mt-1">Número: {selectedPart.part_number}</p>
                </div>
                <button onClick={closeModals} className="text-gray-400 hover:text-gray-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Categoría</label>
                    <p className="text-gray-900">{selectedPart.category}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Stock Actual</label>
                    <p className="text-2xl font-bold text-gray-900">{selectedPart.quantity}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Stock Mínimo</label>
                    <p className="text-gray-900">{selectedPart.minimum_stock}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      selectedPart.quantity === 0 ? 'bg-red-100 text-red-800' :
                      selectedPart.quantity <= selectedPart.minimum_stock ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {selectedPart.quantity === 0 ? 'Sin Stock' :
                       selectedPart.quantity <= selectedPart.minimum_stock ? 'Stock Bajo' : 'Stock Normal'}
                    </span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Costo Unitario</label>
                    <p className="text-gray-900">${selectedPart.unit_cost.toFixed(2)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Valor Total</label>
                    <p className="text-2xl font-bold text-green-600">
                      ${(selectedPart.quantity * selectedPart.unit_cost).toFixed(2)}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ubicación</label>
                    <p className="text-gray-900">{selectedPart.location}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Proveedor</label>
                    <p className="text-gray-900">{selectedPart.supplier || '-'}</p>
                  </div>
                </div>
              </div>
              {selectedPart.description && (
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-900 whitespace-pre-wrap">{selectedPart.description}</p>
                  </div>
                </div>
              )}
              <div className="mt-6 flex justify-end gap-3 pt-4 border-t">
                <button onClick={closeModals} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                  Cerrar
                </button>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    handleAdjustClick(selectedPart);
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Ajustar Stock
                </button>
                <button
                  onClick={() => {
                    setShowDetailModal(false);
                    handleEdit(selectedPart);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Editar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDeleteModal && selectedPart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-lg font-medium text-gray-900">Eliminar Repuesto</h3>
                <p className="mt-2 text-sm text-gray-500">
                  ¿Estás seguro de que deseas eliminar <strong>{selectedPart.name}</strong>? Esta acción no se puede deshacer.
                </p>
                <div className="mt-4 flex justify-end gap-3">
                  <button onClick={closeModals} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
                    Cancelar
                  </button>
                  <button onClick={handleDelete} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryPage;
