import './Auth.css'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'

export default function AdminLogin() {
  const { login, status } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(identifier, password)

      const destination = location.state?.from?.pathname || '/policy/overview'
      navigate(destination, { replace: true })
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  if (status === 'loading') {
    return <p>Checking login session...</p>
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Policy Maker Login</h1>
        <p>Sign in to access the VayuSuchak Policy Maker dashboard.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="identifier">Username or Email</label>
          <input
            id="identifier"
            type="text"
            value={identifier}
            onChange={(event) => setIdentifier(event.target.value)}
            placeholder="Enter username or email"
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter password"
            required
          />

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>

        <p>
          Don't have a Policy Maker account?{' '}
          <Link to="/policy/signup">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
