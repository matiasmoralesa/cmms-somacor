/**
 * WorkOrderErrorBoundary Component
 * 
 * Error boundary specifically for work order components.
 * Catches and handles null reference errors gracefully.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class WorkOrderErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    console.error('Work Order Error Boundary caught an error:', error, errorInfo);

    // Check if it's a null reference error
    const isNullReferenceError =
      error.message.includes('Cannot read properties of null') ||
      error.message.includes('Cannot read property') ||
      error.message.includes('undefined');

    if (isNullReferenceError) {
      console.warn(
        'Null reference error detected in work order component. ' +
        'This might be due to missing asset data.'
      );
    }

    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send error to monitoring service (e.g., Sentry, LogRocket)
    // logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-[200px] flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-6 w-6 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-red-800">
                  Error al cargar la orden de trabajo
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>
                    Algunos datos de las órdenes de trabajo están incompletos o no se pudieron cargar correctamente.
                  </p>
                  {this.state.error?.message.includes('null') && (
                    <p className="mt-2">
                      <strong>Posible causa:</strong> Información de equipo faltante.
                    </p>
                  )}
                </div>
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={this.handleReset}
                    className="text-sm font-medium text-red-800 hover:text-red-900 underline"
                  >
                    Intentar de nuevo
                  </button>
                  <button
                    onClick={() => window.location.reload()}
                    className="text-sm font-medium text-red-800 hover:text-red-900 underline"
                  >
                    Recargar página
                  </button>
                </div>
                
                {/* Show error details in development */}
                {process.env.NODE_ENV === 'development' && this.state.error && (
                  <details className="mt-4">
                    <summary className="text-xs text-red-600 cursor-pointer hover:text-red-700">
                      Detalles técnicos (solo en desarrollo)
                    </summary>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-auto max-h-40">
                      {this.state.error.toString()}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default WorkOrderErrorBoundary;
