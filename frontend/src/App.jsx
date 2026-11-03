import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthProvider'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import AdminLogin from './pages/AdminLogin'
import Dashboard from './pages/Dashboard'
import AQI from './pages/AQI'
import Health from './pages/Health'
import PolicyOverview from './pages/policy/PolicyOverview'
import SourceAnalysis from './pages/policy/SourceAnalysis'
import PolicyInsights from './pages/policy/PolicyInsights'
import PolicyReports from './pages/policy/PolicyReports'

function App() {
  return <BrowserRouter><AuthProvider><Navbar /><main className="app-shell"><Routes><Route path="/dashboard" element={<Dashboard />} /><Route path="/aqi" element={<AQI />} /><Route path="/health" element={<Health />} /><Route path="/admin/login" element={<AdminLogin />} /><Route path="/policy" element={<Navigate to="/policy/overview" replace />} /><Route path="/policy/overview" element={<ProtectedRoute><PolicyOverview /></ProtectedRoute>} /><Route path="/policy/source-analysis" element={<ProtectedRoute><SourceAnalysis /></ProtectedRoute>} /><Route path="/policy/insights" element={<ProtectedRoute><PolicyInsights /></ProtectedRoute>} /><Route path="/policy/reports" element={<ProtectedRoute><PolicyReports /></ProtectedRoute>} /><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes></main></AuthProvider></BrowserRouter>
}

export default App