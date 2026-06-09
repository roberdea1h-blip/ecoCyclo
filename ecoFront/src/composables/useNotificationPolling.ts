import { onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '../stores/notificationStore'

export function useNotificationPolling(intervalMs = 30000) {
  const store = useNotificationStore()
  let timer: ReturnType<typeof setInterval> | null = null

  function start() {
    store.fetchUnreadCount()
    timer = setInterval(() => {
      store.fetchUnreadCount()
    }, intervalMs)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onMounted(() => {
    start()
  })

  onUnmounted(() => {
    stop()
  })

  return {
    unreadCount: store.unreadCount,
    start,
    stop,
  }
}
