<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotificationStore } from '../stores/notificationStore'
import { formatDate } from '../utils/format'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import IconBell from '../components/icons/IconBell.vue'
import IconNotification from '../components/icons/IconNotification.vue'

const notificationStore = useNotificationStore()

onMounted(async () => {
  await notificationStore.fetchNotifications()
})
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Notificaciones</h1>
          <p class="text-gray-600 mt-1">Mantente al tanto de tu actividad</p>
        </div>
        <BaseButton
          v-if="notificationStore.unreadCount > 0"
          variant="secondary"
          size="sm"
          :loading="notificationStore.loading"
          @click="notificationStore.markAllAsRead()"
        >
          Marcar todas como leídas
        </BaseButton>
      </div>

      <BaseSpinner v-if="notificationStore.loading && notificationStore.notifications.length === 0" size="md" />

      <div v-else-if="notificationStore.notifications.length === 0" class="text-center py-12 text-gray-500">
        <IconBell class="w-12 h-12 mx-auto text-gray-300" />
        <p class="text-lg mt-3">Sin notificaciones</p>
        <p class="text-sm mt-1">Aquí aparecerán tus notificaciones</p>
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="notif in notificationStore.notifications"
          :key="notif.id"
          class="transition-colors"
          :class="notif.is_read ? 'opacity-70' : ''"
        >
          <BaseCard padding="sm">
            <div class="flex items-start gap-3">
              <IconNotification class="text-xl shrink-0 mt-0.5" :type="notif.type" />
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <div>
                    <p
                      class="text-sm font-medium"
                      :class="notif.is_read ? 'text-gray-700' : 'text-gray-900'"
                    >
                      {{ notif.title }}
                    </p>
                    <p class="text-sm text-gray-500 mt-0.5">{{ notif.message }}</p>
                  </div>
                  <div class="flex items-center gap-2 shrink-0">
                    <span class="text-xs text-gray-400">{{ formatDate(notif.created_at) }}</span>
                    <button
                      v-if="!notif.is_read"
                      class="text-xs text-emerald-600 hover:text-emerald-700 font-medium shrink-0"
                      @click="notificationStore.markAsRead(notif.id)"
                    >
                      Leído
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
