import type { ApiError } from '../types/api-error'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

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

function parseApiError(data: unknown): ApiError {
  if (
    typeof data === 'object' &&
    data !== null &&
    'error_code' in data &&
    'message' in data
  ) {
    return data as ApiError
  }
  const d = data as Record<string, unknown> | null
  return {
    error_code: 'unknown_error',
    message: (d?.detail as string) || (d?.message as string) || 'Error inesperado',
    details: d,
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
      const error: ApiError = {
        error_code: 'session_expired',
        message: 'Sesión expirada',
      }
      throw error
    }
  }

  if (!res.ok) {
    let errorData: ApiError | null = null
    try {
      const json = await res.json()
      errorData = parseApiError(json)
    } catch {
      errorData = null
    }

    if (
      errorData &&
      (errorData.error_code === 'refresh_token_expired' ||
        errorData.error_code === 'refresh_token_revoked')
    ) {
      const { useAuthStore } = await import('../stores/authStore')
      const authStore = useAuthStore()
      await authStore.logout()
      const { useRouter } = await import('vue-router')
      const router = useRouter()
      router.push('/login')
    }

    throw errorData || {
      error_code: 'unknown_error',
      message: res.statusText || 'Error inesperado',
    }
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
