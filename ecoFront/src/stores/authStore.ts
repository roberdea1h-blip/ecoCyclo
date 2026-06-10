import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import { authApi } from '../api/auth'
import { isApiError } from '../types/api-error'
import { useApiError } from '../composables/useApiError'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const _initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role_name === 'admin')
  const userName = computed(() => user.value?.full_name || user.value?.username || '')
  const userPoints = computed(() => user.value?.points ?? 0)

  const { handleError, clearError } = useApiError()

  function clearUser() {
    user.value = null
  }

  async function initialize() {
    if (_initialized.value) return
    _initialized.value = true
    await fetchUser()
  }

  async function login(email: string, password: string) {
    loading.value = true
    clearError()
    try {
      await authApi.login({ email, password })
      await fetchUser()
    } catch (e: unknown) {
      if (isApiError(e)) {
        if (e.error_code === 'invalid_credentials') {
          error.value = 'Correo o contraseña incorrectos.'
        } else {
          error.value = handleError(e)
        }
      } else {
        error.value = 'Error inesperado. Intenta de nuevo.'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, password: string, full_name: string, username: string) {
    loading.value = true
    clearError()
    try {
      await authApi.register({ email, password, full_name, username })
      await authApi.login({ email, password })
      await fetchUser()
    } catch (e: unknown) {
      error.value = handleError(e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      user.value = await authApi.me()
    } catch {
      user.value = null
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // ignore
    }
    user.value = null
  }

  return {
    user,
    loading,
    error,
    _initialized,
    isAuthenticated,
    isAdmin,
    userName,
    userPoints,
    initialize,
    login,
    register,
    fetchUser,
    logout,
    clearUser,
  }
})
