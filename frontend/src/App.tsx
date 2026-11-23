import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { UploadPapers } from './pages/UploadPapers';
import { PaperAnalysis } from './pages/PaperAnalysis';
import { Predictions } from './pages/Predictions';
import { MockTests } from './pages/MockTests';
import { Settings } from './pages/Settings';
import { SharedQuestionBank } from './pages/SharedQuestionBank';
import { ContributionHistory } from './pages/ContributionHistory';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-xs text-gray-400">
        Authenticating session...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="upload" element={<UploadPapers />} />
              <Route path="shared-bank" element={<SharedQuestionBank />} />
              <Route path="contributions" element={<ContributionHistory />} />
              <Route path="analysis" element={<PaperAnalysis />} />
              <Route path="predictions" element={<Predictions />} />
              <Route path="mocks" element={<MockTests />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
