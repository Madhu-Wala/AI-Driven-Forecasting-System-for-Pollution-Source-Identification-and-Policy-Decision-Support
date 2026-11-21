
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './useAuth'

export default function PolicyRoute() {
  const { status, user } = useAuth()
  const location = useLocation()

  if (status === 'loading') {
    return <p>Checking authentication...</p>
  }

  if (status !== 'authenticated') {
    return (
      <Navigate
        to="/policy/login"
        replace
        state={{ from: location }}
      />
    )
  }

  if (user?.role !== 'policy_maker') {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
