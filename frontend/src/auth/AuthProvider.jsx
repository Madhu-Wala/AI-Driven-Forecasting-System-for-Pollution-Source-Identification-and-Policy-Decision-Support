
import { useCallback, useEffect, useState } from 'react'
import { AuthContext } from './authContext'
import {
  restoreSession,
  signIn,
  signOut,
} from './authService'

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    let active = true

    async function checkSession() {
      const currentUser = await restoreSession()

      if (!active) return

      setUser(currentUser)
      setStatus(currentUser ? 'authenticated' : 'unauthenticated')
    }

    checkSession()

    return () => {
      active = false
    }
  }, [])

  const login = useCallback(async (identifier, password) => {
    setError(null)

    try {
      const loggedInUser = await signIn(identifier, password)

      // Verify the logged-in account is a Policy Maker.
      if (loggedInUser?.role !== 'policy_maker') {
        signOut()
        throw new Error('This account is not authorized for the Policy Maker dashboard.')
      }

      setUser(loggedInUser)
      setStatus('authenticated')

      return loggedInUser
    } catch (err) {
      setError(err.message)
      throw err
    }
  }, [])

  const logout = useCallback(() => {
    signOut()
    setUser(null)
    setError(null)
    setStatus('unauthenticated')
  }, [])

  const value = {
    user,
    status,
    error,
    login,
    logout,
    isAuthenticated: status === 'authenticated',
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
