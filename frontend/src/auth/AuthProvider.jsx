import { useCallback, useEffect, useMemo, useState } from 'react'
import { restoreSession, signIn, signOut } from './authService'
import { AuthContext } from './authContext'

export function AuthProvider({ children }) {
  const [state, setState] = useState({ status: 'loading', user: null, error: '' })

  useEffect(() => {
    let active = true
    restoreSession()
      .then((user) => {
        if (active) setState({ status: user ? 'authenticated' : 'unauthenticated', user, error: '' })
      })
      .catch(() => {
        if (active) setState({ status: 'unauthenticated', user: null, error: 'Your administrator session could not be restored.' })
      })
    return () => { active = false }
  }, [])

  const login = useCallback(async (credentials) => {
    setState((current) => ({ ...current, status: 'loading', error: '' }))
    try {
      const user = await signIn(credentials)
      setState({ status: 'authenticated', user, error: '' })
      return user
    } catch (error) {
      setState({ status: 'unauthenticated', user: null, error: error instanceof Error ? error.message : 'Authentication failed.' })
      throw error
    }
  }, [])

  const logout = useCallback(async () => {
    await signOut()
    setState({ status: 'unauthenticated', user: null, error: '' })
  }, [])

  const value = useMemo(() => ({
    ...state,
    isAuthenticated: state.status === 'authenticated' && Boolean(state.user),
    login,
    logout,
  }), [login, logout, state])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
