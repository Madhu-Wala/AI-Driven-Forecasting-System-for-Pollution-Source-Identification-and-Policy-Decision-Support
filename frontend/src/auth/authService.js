const DEMO_SESSION_KEY = 'vayusuchak_demo_admin_authenticated'
const configuredUsername = import.meta.env.VITE_ADMIN_USERNAME
const configuredPassword = import.meta.env.VITE_ADMIN_PASSWORD
const configurationMessage = 'Administrator demo authentication is not configured. Set VITE_ADMIN_USERNAME and VITE_ADMIN_PASSWORD.'

export class AuthenticationConfigurationError extends Error {
  constructor() {
    super(configurationMessage)
    this.name = 'AuthenticationConfigurationError'
  }
}

export class InvalidCredentialsError extends Error {
  constructor() {
    super('Invalid administrator credentials')
    this.name = 'InvalidCredentialsError'
  }
}

export async function restoreSession() {
  if (sessionStorage.getItem(DEMO_SESSION_KEY) !== 'true') return null
  return { role: 'administrator' }
}

export async function signIn({ identifier, password }) {
  if (!configuredUsername || !configuredPassword) {
    throw new AuthenticationConfigurationError()
  }
  if (identifier !== configuredUsername || password !== configuredPassword) {
    throw new InvalidCredentialsError()
  }
  sessionStorage.setItem(DEMO_SESSION_KEY, 'true')
  return { role: 'administrator' }
}

export async function signOut() {
  sessionStorage.removeItem(DEMO_SESSION_KEY)
}
