import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import logo from '../assets/vayusuchak-logo.png'

export default function AdminLogin() {
  const { error: authError, login, status } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [formError, setFormError] = useState('')
  const isSubmitting = status === 'loading'

  async function handleSubmit(event) {
    event.preventDefault()
    setFormError('')
    if (!identifier.trim() || !password) {
      setFormError('Enter your administrator email or username and password.')
      return
    }

    try {
      await login({ identifier: identifier.trim(), password })
      const destination = location.state?.from
      navigate(destination ? `${destination.pathname}${destination.search || ''}${destination.hash || ''}` : '/policy/overview', { replace: true })
    } catch {
      setPassword('')
    }
  }

  return <div className="auth-page">
    <section className="auth-card card">
      <img className="auth-logo" src={logo} alt="Vayusuchak logo" />
      <span className="eyebrow">Policy Maker access</span>
      <h1>Administrator Login</h1>
      <p className="auth-subtitle">Secure access to the Vayusuchak Policy Dashboard.</p>
      <form className="auth-form" onSubmit={handleSubmit} noValidate>
        <label htmlFor="admin-identifier">Email address or administrator username</label>
        <input id="admin-identifier" value={identifier} onChange={(event) => setIdentifier(event.target.value)} autoComplete="username" required />
        <label htmlFor="admin-password">Password</label>
        <div className="password-field">
          <input id="admin-password" type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
          <button type="button" className="password-toggle" onClick={() => setShowPassword((visible) => !visible)} aria-label={showPassword ? 'Hide password' : 'Show password'}>{showPassword ? 'Hide' : 'Show'}</button>
        </div>
        {(formError || authError) && <p className="auth-error" role="alert">{formError || authError}</p>}
        <button className="button button-primary auth-submit" type="submit" disabled={isSubmitting}>
          {isSubmitting ? <><span className="spinner spinner-light" />Signing in…</> : 'Login'}
        </button>
      </form>
      <p className="auth-notice">Demo authentication is configured for this academic demonstration. Credentials are not stored in browser session data.</p>
    </section>
  </div>
}
