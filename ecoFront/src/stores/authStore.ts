import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const _initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userName = computed(() => user.value?.full_name || user.value?.username || '')
  const userPoints = computed(() => user.value?.points ?? 0)

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
    error.value = null
    try {
      await authApi.login({ email, password })
      await fetchUser()
    } catch (e: any) {
      error.value = e.message || 'Error al iniciar sesión'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, password: string, full_name: string, username: string) {
    loading.value = true
    error.value = null
    try {
      await authApi.register({ email, password, full_name, username })
      await authApi.login({ email, password })
      await fetchUser()
    } catch (e: any) {
      error.value = e.message || 'Error al registrarse'
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
