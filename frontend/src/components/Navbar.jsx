import { NavLink, useLocation } from 'react-router-dom'
import logo from '../assets/vayusuchak-logo.png'

export default function Navbar() {
  const { pathname } = useLocation()
  const isPolicyRoute = pathname.startsWith('/policy')
  const citizenLinks = [['/dashboard', 'Dashboard'], ['/aqi', 'AQI'], ['/health', 'Health']]
  const policyLinks = [
    ['/policy/overview', 'Overview'],
    ['/policy/source-analysis', 'Source Analysis'],
    ['/policy/insights', 'Policy Insights'],
    ['/policy/reports', 'Reports'],
  ]

  return <header className="topbar">
    <div className="brand"><img className="brand-logo" src={logo} alt="Vayusuchak logo" /><span><strong>Vayusuchak</strong><small>Real-time monitoring & forecasting</small></span></div>
    <nav aria-label={isPolicyRoute ? 'Policy Maker navigation' : 'Citizen navigation'}>
      {(isPolicyRoute ? policyLinks : citizenLinks).map(([to, label]) => <NavLink key={to} to={to} end={to === '/policy/overview'} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>{label}</NavLink>)}
    </nav>
    <div className="mode-switch" aria-label="Application mode">
      <NavLink to="/dashboard" className={!isPolicyRoute ? 'mode-active' : ''}>Citizen</NavLink>
      <NavLink to="/policy/overview" className={isPolicyRoute ? 'mode-active' : ''}>Policy Maker</NavLink>
    </div>
  </header>
}
