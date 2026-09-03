import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import AQI from './pages/AQI'
import Health from './pages/Health'

function App() {
  return <BrowserRouter><Navbar /><main className="app-shell"><Routes><Route path="/dashboard" element={<Dashboard />} /><Route path="/aqi" element={<AQI />} /><Route path="/health" element={<Health />} /><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes></main></BrowserRouter>
}

export default App