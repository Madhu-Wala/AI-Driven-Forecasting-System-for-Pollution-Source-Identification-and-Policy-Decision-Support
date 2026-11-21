
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || data.message || 'Something went wrong.')
  }

  return data
}

function saveSession(data) {
  const token = data.access_token || data.token

  if (!token) {
    throw new Error('The server did not return an access token.')
  }

  localStorage.setItem('vayusuchak_access_token', token)

  if (data.user) {
    localStorage.setItem('vayusuchak_user', JSON.stringify(data.user))
  }

  return data.user || null
}

export async function signIn(identifier, password) {
  const data = await request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ identifier, password }),
  })

  const user = saveSession(data)

  return user
}

export async function signUp(formData) {
  return request('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({
      full_name: formData.full_name,
      username: formData.username,
      email: formData.email,
      password: formData.password,
      invitation_code: formData.invitation_code,
    }),
  })
}

export async function restoreSession() {
  const token = localStorage.getItem('vayusuchak_access_token')

  if (!token) {
    return null
  }

  try {
    const data = await request('/api/auth/me', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    const user = data.user || data

    localStorage.setItem('vayusuchak_user', JSON.stringify(user))

    return user
  } catch {
    localStorage.removeItem('vayusuchak_access_token')
    localStorage.removeItem('vayusuchak_user')
    return null
  }
}

export function signOut() {
  localStorage.removeItem('vayusuchak_access_token')
  localStorage.removeItem('vayusuchak_user')
}

export function getAccessToken() {
  return localStorage.getItem('vayusuchak_access_token')
}
