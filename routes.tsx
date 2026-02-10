/**
 * Application routing configuration
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';

// Layout components
const DashboardLayout = lazy(() => import('./components/layout/DashboardLayout'));
const AuthLayout = lazy(() => import('./components/layout/AuthLayout'));

// Page components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const MapView = lazy(() => import('./pages/MapView'));
const Alerts = lazy(() => import('./pages/Alerts'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Reports = lazy(() => import('./pages/Reports'));
const Settings = lazy(() => import('./pages/Settings'));
const Login = lazy(() => import('./pages/Login'));
const Register = lazy(() => import('./pages/Register'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const VillageDetail = lazy(() => import('./pages/VillageDetail'));
const SystemStatus = lazy(() => import('./pages/SystemStatus'));
const DataImport = lazy(() => import('./pages/DataImport'));
const ModelTraining = lazy(() => import('./pages/ModelTraining'));
const APIDocumentation = lazy(() => import('./pages/APIDocumentation'));
const NotFound = lazy(() => import('./pages/NotFound'));

// Loading component
const LoadingFallback = () => (
    <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-gray-300">Loading EQUINOX...</p>
        </div>
    </div>
);

// Protected route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const isAuthenticated = localStorage.getItem('equinox_auth_token'); // Simplified auth check
    
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }
    
    return <>{children}</>;
};

// Public route wrapper (redirect if already authenticated)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
    const isAuthenticated = localStorage.getItem('equinox_auth_token');
    
    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }
    
    return <>{children}</>;
};

// Main application routes
const AppRoutes = () => {
    return (
        <Suspense fallback={<LoadingFallback />}>
            <Routes>
                {/* Public routes */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                <Route path="/login" element={
                    <PublicRoute>
                        <AuthLayout>
                            <Login />
                        </AuthLayout>
                    </PublicRoute>
                } />
                
                <Route path="/register" element={
                    <PublicRoute>
                        <AuthLayout>
                            <Register />
                        </AuthLayout>
                    </PublicRoute>
                } />
                
                <Route path="/forgot-password" element={
                    <PublicRoute>
                        <AuthLayout>
                            <ForgotPassword />
                        </AuthLayout>
                    </PublicRoute>
                } />
                
                {/* Protected routes */}
                <Route path="/dashboard" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <Dashboard />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/map" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <MapView />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/alerts" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <Alerts />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/analytics" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <Analytics />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/reports" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <Reports />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/settings" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <Settings />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/village/:id" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <VillageDetail />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/system" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <SystemStatus />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/data-import" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <DataImport />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/model-training" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <ModelTraining />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                <Route path="/api-docs" element={
                    <ProtectedRoute>
                        <DashboardLayout>
                            <APIDocumentation />
                        </DashboardLayout>
                    </ProtectedRoute>
                } />
                
                {/* Catch-all route */}
                <Route path="*" element={<NotFound />} />
            </Routes>
        </Suspense>
    );
};

// Route configuration for navigation
export const ROUTE_CONFIG = [
    {
        path: '/dashboard',
        label: 'Dashboard',
        icon: '🏠',
        description: 'System overview and key metrics',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/map',
        label: 'Flood Map',
        icon: '🗺️',
        description: 'Interactive flood risk visualization',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/alerts',
        label: 'Alerts',
        icon: '🚨',
        description: 'View and manage flood alerts',
        requiresAuth: true,
        showInNav: true,
        badge: 'count', // Dynamic badge count
    },
    {
        path: '/analytics',
        label: 'Analytics',
        icon: '📊',
        description: 'Detailed flood analytics and reports',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/reports',
        label: 'Reports',
        icon: '📋',
        description: 'View and submit flood reports',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/village/:id',
        label: 'Village Details',
        icon: '🏘️',
        description: 'Detailed village flood information',
        requiresAuth: true,
        showInNav: false, // Not in main nav
    },
    {
        path: '/system',
        label: 'System Status',
        icon: '⚙️',
        description: 'System health and performance',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/data-import',
        label: 'Data Import',
        icon: '📥',
        description: 'Import and manage data sources',
        requiresAuth: true,
        showInNav: false, // Admin only
        adminOnly: true,
    },
    {
        path: '/model-training',
        label: 'ML Training',
        icon: '🧠',
        description: 'Machine learning model management',
        requiresAuth: true,
        showInNav: false, // Admin only
        adminOnly: true,
    },
    {
        path: '/api-docs',
        label: 'API Docs',
        icon: '📚',
        description: 'API documentation and testing',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/settings',
        label: 'Settings',
        icon: '⚙️',
        description: 'Application settings and preferences',
        requiresAuth: true,
        showInNav: true,
    },
    {
        path: '/login',
        label: 'Login',
        icon: '🔐',
        description: 'User authentication',
        requiresAuth: false,
        showInNav: false,
    },
    {
        path: '/register',
        label: 'Register',
        icon: '📝',
        description: 'Create new account',
        requiresAuth: false,
        showInNav: false,
    },
];

// Helper to check if route requires authentication
export function isRouteProtected(path: string): boolean {
    const route = ROUTE_CONFIG.find(r => r.path === path);
    return route ? route.requiresAuth : true; // Default to protected
}

// Helper to get route by path
export function getRouteByPath(path: string) {
    return ROUTE_CONFIG.find(route => route.path === path);
}

// Helper to get navigation routes (for sidebar)
export function getNavigationRoutes(isAdmin: boolean = false) {
    return ROUTE_CONFIG.filter(route => 
        route.showInNav && 
        (!route.adminOnly || (route.adminOnly && isAdmin))
    );
}

// Generate breadcrumbs for current path
export function generateBreadcrumbs(pathname: string) {
    const segments = pathname.split('/').filter(segment => segment);
    const breadcrumbs = [];
    
    let currentPath = '';
    for (const segment of segments) {
        currentPath += `/${segment}`;
        const route = getRouteByPath(currentPath);
        
        if (route) {
            breadcrumbs.push({
                label: route.label,
                href: currentPath,
            });
        } else {
            // For dynamic segments like :id
            breadcrumbs.push({
                label: segment.charAt(0).toUpperCase() + segment.slice(1),
                href: currentPath,
            });
        }
    }
    
    return breadcrumbs;
}

export default AppRoutes;