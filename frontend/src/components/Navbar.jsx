import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import logo from '../assets/vayusuchak-logo.png'

export default function Navbar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, logout } = useAuth()
  const isPolicyRoute = pathname.startsWith('/policy')
  const showPolicyNavigation = isPolicyRoute && isAuthenticated
  const citizenLinks = [['/dashboard', 'Dashboard'], ['/aqi', 'AQI'], ['/health', 'Health']]
  const policyLinks = [
    ['/policy/overview', 'Overview'],
    ['/policy/source-analysis', 'Source Analysis'],
    ['/policy/insights', 'Policy Insights'],
    ['/policy/reports', 'Reports'],
  ]

  return <header className="topbar">
    <div className="brand"><img className="brand-logo" src={logo} alt="Vayusuchak logo" /><span><strong>Vayusuchak</strong><small>Real-time monitoring & forecasting</small></span></div>
    <nav aria-label={showPolicyNavigation ? 'Policy Maker navigation' : 'Citizen navigation'}>
      {(showPolicyNavigation ? policyLinks : citizenLinks).map(([to, label]) => <NavLink key={to} to={to} end={to === '/policy/overview'} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>{label}</NavLink>)}
    </nav>
    <div className="mode-switch" aria-label="Application mode">
      <NavLink to="/dashboard" className={!isPolicyRoute ? 'mode-active' : ''}>Citizen</NavLink>
      <NavLink to={isAuthenticated ? '/policy/overview' : '/admin/login'} className={isPolicyRoute ? 'mode-active' : ''}>Policy Maker</NavLink>
    </div>
    {isAuthenticated && <div className="admin-session"><span className="admin-indicator" aria-hidden="true">A</span><span className="admin-label">Administrator</span><button type="button" className="logout-button" onClick={() => { logout(); navigate('/admin/login', { replace: true }) }}>Logout</button></div>}
  </header>
}
