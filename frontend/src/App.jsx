import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import AQI from './pages/AQI'
import Health from './pages/Health'
import PolicyOverview from './pages/policy/PolicyOverview'
import SourceAnalysis from './pages/policy/SourceAnalysis'
import PolicyInsights from './pages/policy/PolicyInsights'
import PolicyReports from './pages/policy/PolicyReports'

function App() {
  return <BrowserRouter><Navbar /><main className="app-shell"><Routes><Route path="/dashboard" element={<Dashboard />} /><Route path="/aqi" element={<AQI />} /><Route path="/health" element={<Health />} /><Route path="/policy" element={<Navigate to="/policy/overview" replace />} /><Route path="/policy/overview" element={<PolicyOverview />} /><Route path="/policy/source-analysis" element={<SourceAnalysis />} /><Route path="/policy/insights" element={<PolicyInsights />} /><Route path="/policy/reports" element={<PolicyReports />} /><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes></main></BrowserRouter>
}

export default App