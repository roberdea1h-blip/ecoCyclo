import { api } from './http'
import type { Notification } from '../types'

export const notificationsApi = {
  list() {
    return api.get<Notification[]>('/notifications')
  },

  unread() {
    return api.get<Notification[]>('/notifications/unread')
  },

  unreadCount() {
    return api.get<{ count: number }>('/notifications/unread/count')
  },

  markRead(id: string) {
    return api.patch<void>(`/notifications/${id}/read`)
  },

  markAllRead() {
    return api.patch<void>('/notifications/read-all')
  },
}
