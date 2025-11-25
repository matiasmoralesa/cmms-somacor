/**
 * Configuration Page
 */
import React, { useState } from 'react';
import AssetCategoryManager from '../components/config/AssetCategoryManager';
import LocationManager from '../components/config/LocationManager';
import PriorityManager from '../components/config/PriorityManager';
import WorkOrderTypeManager from '../components/config/WorkOrderTypeManager';
import SystemParameterManager from '../components/config/SystemParameterManager';
import AuditLogViewer from '../components/config/AuditLogViewer';
import UserManager from '../components/config/UserManager';

const Configuration: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('categories');

  const tabs = [
    { id: 'categories', name: 'Categorías', icon: '📁' },
    { id: 'locations', name: 'Ubicaciones', icon: '📍' },
    { id: 'priorities', name: 'Prioridades', icon: '🎯' },
    { id: 'work-order-types', name: 'Tipos de OT', icon: '📋' },
    { id: 'users', name: 'Usuarios', icon: '👥' },
    { id: 'parameters', name: 'Parámetros', icon: '⚙️' },
    { id: 'audit', name: 'Auditoría', icon: '📜' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración del Sistema</h1>
        <p className="mt-1 text-sm text-gray-600">
          Gestión de datos maestros y parámetros del sistema
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="card p-6">
        {activeTab === 'categories' && <AssetCategoryManager />}
        {activeTab === 'locations' && <LocationManager />}
        {activeTab === 'priorities' && <PriorityManager />}
        {activeTab === 'work-order-types' && <WorkOrderTypeManager />}
        {activeTab === 'users' && <UserManager />}
        {activeTab === 'parameters' && <SystemParameterManager />}
        {activeTab === 'audit' && <AuditLogViewer />}
      </div>
    </div>
  );
};

export default Configuration;
