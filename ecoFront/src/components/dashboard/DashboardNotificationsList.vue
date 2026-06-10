<script setup lang="ts">
import { computed } from 'vue'
import { useNotificationStore } from '../../stores/notificationStore'
import { formatDate } from '../../utils/format'
import BaseCard from '../base/BaseCard.vue'
import IconNotification from '../icons/IconNotification.vue'

const notificationStore = useNotificationStore()

const recentNotifications = computed(() => (notificationStore.notifications || []).slice(0, 5))
</script>

<template>
  <BaseCard>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Notificaciones recientes</h2>
      <router-link to="/notifications" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
        Ver todas
      </router-link>
    </div>
    <div v-if="recentNotifications.length === 0" class="text-center py-12 text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto mb-3">
        <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z" />
      </svg>
      <p class="text-lg font-medium text-gray-500">Sin notificaciones</p>
    </div>
    <div v-else class="space-y-2">
      <div
        v-for="notif in recentNotifications"
        :key="notif.id"
        class="p-3 rounded-lg"
        :class="notif.is_read ? 'bg-gray-50' : 'bg-blue-50'"
      >
        <div class="flex items-start gap-3">
          <IconNotification class="text-lg shrink-0" :type="notif.type" />
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-900">{{ notif.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ notif.message }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ formatDate(notif.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </BaseCard>
</template>
