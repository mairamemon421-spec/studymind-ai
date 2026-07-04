import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './lib/auth';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { SubjectsPage } from './pages/SubjectsPage';
import { PlanPage } from './pages/PlanPage';
import { TutorPage } from './pages/TutorPage';
import { QuizPage } from './pages/QuizPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AgentLogsPage } from './pages/AgentLogsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="subjects" element={<SubjectsPage />} />
            <Route path="plan" element={<PlanPage />} />
            <Route path="tutor" element={<TutorPage />} />
            <Route path="quiz" element={<QuizPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="logs" element={<AgentLogsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#0a0a1a',
            color: '#e2e8f0',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '12px',
          },
        }}
      />
    </AuthProvider>
  );
}

export default App;
