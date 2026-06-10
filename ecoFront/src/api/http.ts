const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

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
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    })
    return res.ok
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
  const headers: Record<string, string> = {}

  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const opts: RequestInit = { method, headers, credentials: 'include' }

  if (body) {
    opts.body = isFormData ? (body as FormData) : JSON.stringify(body)
  }

  let res = await fetch(`${API_BASE}${path}`, opts)

  if (res.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      res = await fetch(`${API_BASE}${path}`, opts)
    } else {
      const { useAuthStore } = await import('../stores/authStore')
      const authStore = useAuthStore()
      authStore.clearUser()
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
