import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '../types'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userName = computed(() => user.value?.full_name || user.value?.username || '')
  const userPoints = computed(() => user.value?.points ?? 0)

  function setTokens(access: string, refresh: string) {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function clearUser() {
    user.value = null
  }

  function clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(email: string, password: string) {
    loading.value = true
    error.value = null
    try {
      const tokens = await authApi.login({ email, password })
      setTokens(tokens.access_token, tokens.refresh_token)
      await fetchUser()
    } catch (e: any) {
      error.value = e.message || 'Error al iniciar sesión'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(email: string, password: string, full_name: string) {
    loading.value = true
    error.value = null
    try {
      const tokens = await authApi.register({ email, password, full_name })
      setTokens(tokens.access_token, tokens.refresh_token)
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
      clearTokens()
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // ignore
    }
    user.value = null
    clearTokens()
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    userName,
    userPoints,
    login,
    register,
    fetchUser,
    logout,
    clearUser,
    clearTokens,
  }
})
