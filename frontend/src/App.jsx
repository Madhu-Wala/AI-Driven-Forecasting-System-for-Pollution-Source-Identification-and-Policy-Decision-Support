
import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import AdminLogin from './pages/AdminLogin'
import AdminSignup from './pages/AdminSignup'
import Dashboard from './pages/Dashboard'
import AQI from './pages/AQI'
import Health from './pages/Health'
import PolicyOverview from './pages/policy/PolicyOverview'
import SourceAnalysis from './pages/policy/SourceAnalysis'
import PolicyInsights from './pages/policy/PolicyInsights'
import PolicyReports from './pages/policy/PolicyReports'
import PolicyRoute from './auth/PolicyRoute'

function App() {
  return (
    <>
      <Navbar />

      <main className="app-shell">
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/aqi" element={<AQI />} />
          <Route path="/health" element={<Health />} />

          <Route path="/policy/login" element={<AdminLogin />} />
          <Route path="/policy/signup" element={<AdminSignup />} />
          <Route
            path="/policy"
            element={<Navigate to="/policy/overview" replace />}
          />

          <Route element={<PolicyRoute />}>
            <Route
              path="/policy/overview"
              element={<ProtectedRoute><PolicyOverview /></ProtectedRoute>}
            />
            <Route
              path="/policy/source-analysis"
              element={<ProtectedRoute><SourceAnalysis /></ProtectedRoute>}
            />
            <Route
              path="/policy/insights"
              element={<ProtectedRoute><PolicyInsights /></ProtectedRoute>}
            />
            <Route
              path="/policy/reports"
              element={<ProtectedRoute><PolicyReports /></ProtectedRoute>}
            />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </>
  )
}

export default App
