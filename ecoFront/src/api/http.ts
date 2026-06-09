const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

function getTokens() {
  return {
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
  }
}

function setTokens(access: string, refresh: string) {
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function refreshAccessToken(): Promise<boolean> {
  const { refreshToken } = getTokens()
  if (!refreshToken) return false

  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!res.ok) return false

    const data = await res.json()
    setTokens(data.access_token, data.refresh_token)
    return true
  } catch {
    return false
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  isFormData?: boolean
): Promise<T> {
  const { accessToken } = getTokens()
  const headers: Record<string, string> = {}

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const opts: RequestInit = { method, headers }

  if (body) {
    opts.body = isFormData ? (body as FormData) : JSON.stringify(body)
  }

  let res = await fetch(`${API_BASE}${path}`, opts)

  if (res.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      const { accessToken: newToken } = getTokens()
      headers['Authorization'] = `Bearer ${newToken}`
      res = await fetch(`${API_BASE}${path}`, { ...opts, headers })
    } else {
      clearTokens()
      const { useAuthStore } = await import('../stores/authStore')
      const authStore = useAuthStore()
      authStore.clearUser()
      window.location.href = '/login'
      throw new ApiError(401, 'Sesión expirada')
    }
  }

  if (!res.ok) {
    let errorData: { detail?: string; message?: string } | null = null
    try {
      errorData = await res.json()
    } catch {
      errorData = null
    }
    throw new ApiError(
      res.status,
      errorData?.detail || errorData?.message || res.statusText,
      errorData
    )
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json()
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  postForm: <T>(path: string, body: FormData) => request<T>('POST', path, body, true),
  patch: <T>(path: string, body?: unknown) => request<T>('PATCH', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
}
