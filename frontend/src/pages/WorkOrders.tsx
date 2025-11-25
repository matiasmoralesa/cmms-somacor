/**
 * Work Orders Page
 */
import React, { useState, useEffect } from 'react';
import workOrderService from '../services/workOrderService';
import WorkOrderForm from '../components/work-orders/WorkOrderForm';
import type { WorkOrder } from '../types/workOrder.types';
import { hasAsset, formatAssetInfo } from '../utils/workOrderHelpers';

const WorkOrdersPage: React.FC = () => {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [filteredWorkOrders, setFilteredWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<WorkOrder | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  useEffect(() => {
    loadWorkOrders();
  }, []);

  useEffect(() => {
    filterWorkOrders();
  }, [workOrders, searchTerm, statusFilter]);

  const loadWorkOrders = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await workOrderService.getWorkOrders();
      setWorkOrders(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Error loading work orders:', err);
      setError(err.response?.data?.message || err.message || 'Error al cargar las órdenes de trabajo');
      setWorkOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const filterWorkOrders = () => {
    let filtered = [...workOrders];

    // Filter by status
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(wo => wo.status === statusFilter);
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(wo =>
        wo.work_order_number.toLowerCase().includes(term) ||
        wo.title.toLowerCase().includes(term) ||
        wo.asset_name?.toLowerCase().includes(term) ||
        wo.assigned_to_name?.toLowerCase().includes(term)
      );
    }

    setFilteredWorkOrders(filtered);
  };

  const handleRowClick = (workOrder: WorkOrder) => {
    setSelectedWorkOrder(workOrder);
    setShowDetailModal(true);
  };

  const handleCreateNew = () => {
    setShowCreateModal(true);
  };

  const handleCloseModals = () => {
    setShowCreateModal(false);
    setShowDetailModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
    setSelectedWorkOrder(null);
  };

  const handleCreate = async (data: Partial<WorkOrder>) => {
    await workOrderService.createWorkOrder(data as any);
    handleCloseModals();
    loadWorkOrders();
  };

  const handleUpdate = async (data: Partial<WorkOrder>) => {
    if (selectedWorkOrder) {
      await workOrderService.updateWorkOrder(selectedWorkOrder.id, data);
      handleCloseModals();
      loadWorkOrders();
    }
  };

  const handleDelete = async () => {
    if (selectedWorkOrder) {
      try {
        await workOrderService.deleteWorkOrder(selectedWorkOrder.id);
        handleCloseModals();
        loadWorkOrders();
      } catch (err: any) {
        alert(err.response?.data?.message || 'Error al eliminar la orden de trabajo');
      }
    }
  };

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const handleEdit = (workOrder: WorkOrder) => {
    setSelectedWorkOrder(workOrder);
    setShowEditModal(true);
  };

  const handleDeleteClick = (workOrder: WorkOrder) => {
    setSelectedWorkOrder(workOrder);
    setShowDeleteModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Cargando órdenes de trabajo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <svg
            className="w-6 h-6 text-red-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <button
              onClick={loadWorkOrders}
              className="mt-3 text-sm font-medium text-red-800 hover:text-red-900 underline"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Órdenes de Trabajo</h1>
            <p className="text-gray-600 mt-1">
              Gestiona y da seguimiento a las órdenes de trabajo
            </p>
          </div>
          <button 
            onClick={handleCreateNew}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Nueva Orden
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Buscar
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por número, título, equipo o asignado..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filtrar por Estado
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="ALL">Todos los estados</option>
                <option value="PENDING">Pendiente</option>
                <option value="ASSIGNED">Asignado</option>
                <option value="IN_PROGRESS">En Progreso</option>
                <option value="COMPLETED">Completado</option>
                <option value="CANCELLED">Cancelado</option>
              </select>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('ALL')}>
            <p className="text-sm text-gray-600">Total</p>
            <p className="text-2xl font-bold text-gray-900">{workOrders.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('PENDING')}>
            <p className="text-sm text-gray-600">Pendientes</p>
            <p className="text-2xl font-bold text-yellow-600">
              {workOrders.filter((wo) => wo.status === 'PENDING').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('IN_PROGRESS')}>
            <p className="text-sm text-gray-600">En Progreso</p>
            <p className="text-2xl font-bold text-blue-600">
              {workOrders.filter((wo) => wo.status === 'IN_PROGRESS').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Sin Equipo</p>
            <p className="text-2xl font-bold text-orange-600">
              {workOrders.filter((wo) => !hasAsset(wo)).length}
            </p>
          </div>
        </div>

        {/* Work Orders List */}
        {filteredWorkOrders.length === 0 ? (
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
              {searchTerm || statusFilter !== 'ALL' ? 'No se encontraron órdenes de trabajo' : 'No hay órdenes de trabajo'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {searchTerm || statusFilter !== 'ALL' ? 'Intenta ajustar los filtros de búsqueda' : 'Comienza creando una nueva orden de trabajo'}
            </p>
            {(searchTerm || statusFilter !== 'ALL') && (
              <button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('ALL');
                }}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Limpiar filtros
              </button>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
              <p className="text-sm text-gray-700">
                Mostrando <span className="font-medium">{filteredWorkOrders.length}</span> de <span className="font-medium">{workOrders.length}</span> órdenes de trabajo
              </p>
            </div>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Número
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Título
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Equipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prioridad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Asignado a
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredWorkOrders.map((workOrder) => (
                  <tr 
                    key={workOrder.id} 
                    onClick={() => handleRowClick(workOrder)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {workOrder.work_order_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {workOrder.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {hasAsset(workOrder) ? (
                        <span className="text-gray-900">
                          {formatAssetInfo(workOrder)}
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-yellow-600">
                          <svg
                            className="w-4 h-4"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                              clipRule="evenodd"
                            />
                          </svg>
                          Sin equipo
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {workOrder.work_order_type_display}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          workOrder.priority === 'URGENT'
                            ? 'bg-red-100 text-red-800'
                            : workOrder.priority === 'HIGH'
                            ? 'bg-orange-100 text-orange-800'
                            : workOrder.priority === 'MEDIUM'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {workOrder.priority_display}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          workOrder.status === 'COMPLETED'
                            ? 'bg-green-100 text-green-800'
                            : workOrder.status === 'IN_PROGRESS'
                            ? 'bg-blue-100 text-blue-800'
                            : workOrder.status === 'CANCELLED'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {workOrder.status_display}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {workOrder.assigned_to_name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(workOrder);
                        }}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Editar
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(workOrder);
                        }}
                        className="text-red-600 hover:text-red-900"
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Nueva Orden de Trabajo</h2>
                  <button
                    onClick={handleCloseModals}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <WorkOrderForm onSubmit={handleCreate} onCancel={handleCloseModals} />
              </div>
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {showEditModal && selectedWorkOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Editar Orden de Trabajo</h2>
                  <button
                    onClick={handleCloseModals}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <WorkOrderForm workOrder={selectedWorkOrder} onSubmit={handleUpdate} onCancel={handleCloseModals} />
              </div>
            </div>
          </div>
        )}

        {/* Detail Modal */}
        {showDetailModal && selectedWorkOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{selectedWorkOrder.title}</h2>
                    <p className="text-sm text-gray-500 mt-1">OT #{selectedWorkOrder.work_order_number}</p>
                  </div>
                  <button
                    onClick={handleCloseModals}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Left Column */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                      <span
                        className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${
                          selectedWorkOrder.status === 'COMPLETED'
                            ? 'bg-green-100 text-green-800'
                            : selectedWorkOrder.status === 'IN_PROGRESS'
                            ? 'bg-blue-100 text-blue-800'
                            : selectedWorkOrder.status === 'CANCELLED'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {selectedWorkOrder.status_display}
                      </span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Prioridad</label>
                      <span
                        className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${
                          selectedWorkOrder.priority === 'URGENT'
                            ? 'bg-red-100 text-red-800'
                            : selectedWorkOrder.priority === 'HIGH'
                            ? 'bg-orange-100 text-orange-800'
                            : selectedWorkOrder.priority === 'MEDIUM'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {selectedWorkOrder.priority_display}
                      </span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
                      <p className="text-gray-900">{selectedWorkOrder.work_order_type_display}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Equipo</label>
                      <p className="text-gray-900">
                        {hasAsset(selectedWorkOrder) ? formatAssetInfo(selectedWorkOrder) : 'Sin equipo asignado'}
                      </p>
                    </div>
                  </div>

                  {/* Right Column */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Asignado a</label>
                      <p className="text-gray-900">{selectedWorkOrder.assigned_to_name || 'Sin asignar'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Creado por</label>
                      <p className="text-gray-900">{selectedWorkOrder.created_by_name || '-'}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Fecha programada</label>
                      <p className="text-gray-900">
                        {selectedWorkOrder.scheduled_date 
                          ? new Date(selectedWorkOrder.scheduled_date).toLocaleString('es-ES')
                          : 'No programada'}
                      </p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Horas estimadas</label>
                      <p className="text-gray-900">{selectedWorkOrder.estimated_hours || '-'} horas</p>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-900 whitespace-pre-wrap">{selectedWorkOrder.description || 'Sin descripción'}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="mt-6 flex justify-end gap-3">
                  <button
                    onClick={handleCloseModals}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                  >
                    Cerrar
                  </button>
                  <button
                    onClick={() => {
                      setShowDetailModal(false);
                      handleEdit(selectedWorkOrder);
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

        {/* Delete Confirmation Modal */}
        {showDeleteModal && selectedWorkOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">Eliminar Orden de Trabajo</h3>
                  <p className="mt-2 text-sm text-gray-500">
                    ¿Estás seguro de que deseas eliminar la orden <strong>{selectedWorkOrder.work_order_number}</strong>? Esta acción no se puede deshacer.
                  </p>
                  <div className="mt-4 flex justify-end gap-3">
                    <button onClick={handleCloseModals} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">
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

export default WorkOrdersPage;
