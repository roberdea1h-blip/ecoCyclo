import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification } from '../types'
import { notificationsApi } from '../api/notifications'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchNotifications() {
    loading.value = true
    error.value = null
    try {
      notifications.value = await notificationsApi.list()
    } catch (e: any) {
      error.value = e.message || 'Error al cargar notificaciones'
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

  async function markAsRead(id: number) {
    try {
      await notificationsApi.markRead(id)
      const notif = notifications.value.find(n => n.id === id)
      if (notif) notif.is_read = true
      if (unreadCount.value > 0) unreadCount.value -= 1
    } catch (e: any) {
      error.value = e.message || 'Error al marcar notificación'
    }
  }

  async function markAllAsRead() {
    try {
      await notificationsApi.markAllRead()
      notifications.value.forEach(n => (n.is_read = true))
      unreadCount.value = 0
    } catch (e: any) {
      error.value = e.message || 'Error al marcar todas'
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
