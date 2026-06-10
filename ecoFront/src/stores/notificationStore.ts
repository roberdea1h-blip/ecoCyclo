import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification } from '../types'
import { notificationsApi } from '../api/notifications'
import { useApiError } from '../composables/useApiError'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleError, clearError } = useApiError()

  async function fetchNotifications() {
    loading.value = true
    clearError()
    try {
      notifications.value = await notificationsApi.list()
    } catch (e: unknown) {
      error.value = handleError(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const result = await notificationsApi.unreadCount()
      unreadCount.value = result.count
    } catch {
      // silent
    }
  }

  async function markAsRead(id: string) {
    try {
      await notificationsApi.markRead(id)
      const notif = notifications.value.find(n => n.id === id)
      if (notif) notif.is_read = true
      if (unreadCount.value > 0) unreadCount.value -= 1
    } catch (e: unknown) {
      error.value = handleError(e)
    }
  }

  async function markAllAsRead() {
    try {
      await notificationsApi.markAllRead()
      notifications.value.forEach(n => (n.is_read = true))
      unreadCount.value = 0
    } catch (e: unknown) {
      error.value = handleError(e)
    }
  }

  return {
    notifications,
    unreadCount,
    loading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
  }
})
