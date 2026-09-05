import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Layouts
import StudentLayout from './layouts/StudentLayout';
import AdminLayout from './layouts/AdminLayout';

// Public Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Student Pages
import Dashboard from './pages/student/Dashboard';
import Profile from './pages/student/Profile';
import Companies from './pages/student/Companies';
import CompanyDetail from './pages/student/CompanyDetail';
import SkillGap from './pages/student/SkillGap';
import Roadmap from './pages/student/Roadmap';
import DailyTasks from './pages/student/DailyTasks';
import Practice from './pages/student/Practice';
import TestRunner from './pages/student/TestRunner';
import TestResult from './pages/student/TestResult';
import MockInterview from './pages/student/MockInterview';
import ResumeAnalysis from './pages/student/ResumeAnalysis';
import Projects from './pages/student/Projects';
import Progress from './pages/student/Progress';
import CompanyComparison from './pages/student/CompanyComparison';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminCompanies from './pages/admin/AdminCompanies';
import AdminQuestions from './pages/admin/AdminQuestions';
import AdminWeights from './pages/admin/AdminWeights';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Student Protected Routes */}
          <Route element={<StudentLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/companies/:id" element={<CompanyDetail />} />
            <Route path="/skill-gap" element={<SkillGap />} />
            <Route path="/roadmap" element={<Roadmap />} />
            <Route path="/tasks" element={<DailyTasks />} />
            <Route path="/practice" element={<Practice />} />
            <Route path="/test/:id" element={<TestRunner />} />
            <Route path="/test/:id/result" element={<TestResult />} />
            <Route path="/mock-interview" element={<MockInterview />} />
            <Route path="/resume" element={<ResumeAnalysis />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/compare" element={<CompanyComparison />} />
          </Route>

          {/* Admin Protected Routes */}
          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/companies" element={<AdminCompanies />} />
            <Route path="/admin/questions" element={<AdminQuestions />} />
            <Route path="/admin/weights" element={<AdminWeights />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
