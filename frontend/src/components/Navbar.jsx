import { NavLink } from 'react-router-dom'
import logo from '../assets/vayusuchak-logo.png'

export default function Navbar() {
  return <header className="topbar"><div className="brand"><img className="brand-logo" src={logo} alt="Vayusuchak logo" /><span><strong>Vayusuchak</strong><small>Real-time monitoring & forecasting</small></span></div><nav>{[['/dashboard', 'Dashboard'], ['/aqi', 'AQI'], ['/health', 'Health']].map(([to, label]) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>{label}</NavLink>)}</nav><div className="mode-switch"><span className="mode-active">Citizen</span><span>Policy Maker</span></div></header>
}
