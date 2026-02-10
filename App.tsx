import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './styles/globals.css';

// Import components
 import{ Header }from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import MapView from './pages/MapView';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import SystemStatus from './pages/SystemStatus';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// Import contexts
import { AlertProvider } from './contexts/AlertContext';
import { DataProvider } from './contexts/DataContext';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true); // For demo, always authenticated
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('equinox_auth_token');
    setIsAuthenticated(!!token);
  }, []);

  // Handle theme
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  // Protected route wrapper
  const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return <>{children}</>;
  };

  // Public route wrapper (redirect if already authenticated)
  const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    if (isAuthenticated) {
      return <Navigate to="/dashboard" replace />;
    }
    return <>{children}</>;
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <Router>
      <AlertProvider>
        <DataProvider>
          <div className={`app ${theme} ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
            {/* Login page has different layout */}
            <Routes>
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <Login onLogin={() => setIsAuthenticated(true)} />
                  </PublicRoute>
                } 
              />
              
              <Route path="*" element={
                isAuthenticated ? (
                  <div className="app-layout">
                    <Header 
                      onMenuClick={toggleSidebar}
                      onThemeToggle={toggleTheme}
                      theme={theme}
                    />
                    
                    <div className="main-content">
                      <Sidebar 
                        collapsed={sidebarCollapsed}
                        onToggle={toggleSidebar}
                      />
                      
                      <div className="content-area">
                        <Routes>
                          <Route path="/" element={<Navigate to="/dashboard" replace />} />
                          <Route 
                            path="/dashboard" 
                            element={
                              <ProtectedRoute>
                                <Dashboard />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/map" 
                            element={
                              <ProtectedRoute>
                                <MapView />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/alerts" 
                            element={
                              <ProtectedRoute>
                                <Alerts />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/analytics" 
                            element={
                              <ProtectedRoute>
                                <Analytics />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/reports" 
                            element={
                              <ProtectedRoute>
                                <Reports />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/settings" 
                            element={
                              <ProtectedRoute>
                                <Settings />
                              </ProtectedRoute>
                            } 
                          />
                          <Route 
                            path="/system" 
                            element={
                              <ProtectedRoute>
                                <SystemStatus />
                              </ProtectedRoute>
                            } 
                          />
                          <Route path="*" element={<NotFound />} />
                        </Routes>
                      </div>
                    </div>
                  </div>
                ) : (
                  <Navigate to="/login" replace />
                )
              } />
            </Routes>
          </div>
        </DataProvider>
      </AlertProvider>
    </Router>
  );
}

export default App;