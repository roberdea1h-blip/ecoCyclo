import { computed } from 'vue'
import { useAuthStore } from '../stores/authStore'

export function useAuth() {
  const store = useAuthStore()

  return {
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isAdmin: computed(() => store.isAdmin),
    userName: computed(() => store.userName),
    userPoints: computed(() => store.userPoints),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    login: store.login,
    register: store.register,
    logout: store.logout,
    fetchUser: store.fetchUser,
  }
}
