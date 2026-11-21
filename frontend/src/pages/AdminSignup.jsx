
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { signUp } from '../auth/authService'
import './Auth.css'
export default function AdminSignup() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    invitation_code: '',
  })

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.')
      return
    }

    if (formData.password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    setLoading(true)

    try {
      await signUp(formData)

      setSuccess('Account created successfully. You can now log in.')

      setTimeout(() => {
        navigate('/policy/login', {
          replace: true,
          state: { signupSuccess: true },
        })
      }, 1200)
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Policy Maker Signup</h1>
        <p>Create an account to access the VayuSuchak Policy Maker dashboard.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="full_name">Full Name</label>
          <input
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Enter your full name"
            required
          />

          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Choose a username"
            required
          />

          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter your email"
            required
          />

          <label htmlFor="signup-password">Password</label>
          <input
            id="signup-password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="At least 8 characters"
            minLength={8}
            required
          />

          <label htmlFor="confirm_password">Confirm Password</label>
          <input
            id="confirm_password"
            name="confirm_password"
            type="password"
            value={formData.confirm_password}
            onChange={handleChange}
            placeholder="Re-enter your password"
            required
          />

          <label htmlFor="invitation_code">Invitation Code</label>
          <input
            id="invitation_code"
            name="invitation_code"
            type="password"
            value={formData.invitation_code}
            onChange={handleChange}
            placeholder="Enter Policy Maker invitation code"
            required
          />

          {error && <p className="auth-error">{error}</p>}
          {success && <p className="auth-success">{success}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p>
          Already have an account?{' '}
          <Link to="/policy/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
