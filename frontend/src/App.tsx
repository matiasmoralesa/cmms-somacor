import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Checklists from './pages/Checklists';
import Assets from './pages/Assets';
import WorkOrders from './pages/WorkOrders';
import Maintenance from './pages/Maintenance';
import Inventory from './pages/Inventory';
import Predictions from './pages/Predictions';
import Admin from './pages/Admin';
import Notifications from './pages/Notifications';
import Reports from './pages/Reports';
import LocationsPage from './pages/LocationsPage';
import UsersPage from './pages/UsersPage';
import MachineStatusPage from './pages/MachineStatusPage';
import ToastContainer from './components/notifications/ToastContainer';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const { loadUser } = useAuthStore();

  useEffect(() => {
    // Load user from localStorage on app start
    loadUser();
  }, [loadUser]);

  return (
    <BrowserRouter>
      <ToastContainer />
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route element={<ProtectedRoute />}>
          <Route
            path="/dashboard"
            element={
              <Layout>
                <Dashboard />
              </Layout>
            }
          />
          <Route
            path="/checklists"
            element={
              <Layout>
                <Checklists />
              </Layout>
            }
          />
          <Route
            path="/assets"
            element={
              <Layout>
                <Assets />
              </Layout>
            }
          />
          <Route
            path="/work-orders"
            element={
              <Layout>
                <WorkOrders />
              </Layout>
            }
          />
          <Route
            path="/maintenance"
            element={
              <Layout>
                <Maintenance />
              </Layout>
            }
          />
          <Route
            path="/inventory"
            element={
              <Layout>
                <ErrorBoundary>
                  <Inventory />
                </ErrorBoundary>
              </Layout>
            }
          />
          <Route
            path="/predictions"
            element={
              <Layout>
                <Predictions />
              </Layout>
            }
          />
          <Route
            path="/admin"
            element={
              <Layout>
                <Admin />
              </Layout>
            }
          />
          <Route
            path="/notifications"
            element={
              <Layout>
                <Notifications />
              </Layout>
            }
          />
          <Route
            path="/reports"
            element={
              <Layout>
                <Reports />
              </Layout>
            }
          />
          <Route
            path="/locations/*"
            element={
              <Layout>
                <LocationsPage />
              </Layout>
            }
          />
          <Route
            path="/users/*"
            element={
              <Layout>
                <UsersPage />
              </Layout>
            }
          />
          <Route
            path="/machine-status/*"
            element={
              <Layout>
                <MachineStatusPage />
              </Layout>
            }
          />
        </Route>

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        
        <Route
          path="/unauthorized"
          element={
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-10 h-10 text-red-600"
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
                </div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">403</h1>
                <p className="text-gray-600 mb-6">
                  No tienes permisos para acceder a esta página
                </p>
                <button
                  onClick={() => window.history.back()}
                  className="btn btn-primary"
                >
                  Volver
                </button>
              </div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
