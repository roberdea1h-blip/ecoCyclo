<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useReportStore } from '../stores/reportStore'
import { useNotificationStore } from '../stores/notificationStore'
import { formatPoints, getStatusLabel, formatDate } from '../utils/format'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import IconGift from '../components/icons/IconGift.vue'
import IconReport from '../components/icons/IconReport.vue'
import IconStar from '../components/icons/IconStar.vue'
import IconBell from '../components/icons/IconBell.vue'
import IconUser from '../components/icons/IconUser.vue'
import IconNotification from '../components/icons/IconNotification.vue'

const authStore = useAuthStore()
const reportStore = useReportStore()
const notificationStore = useNotificationStore()

onMounted(async () => {
  await Promise.all([
    reportStore.fetchMyReports(),
    notificationStore.fetchNotifications(),
  ])
})

const recentNotifications = notificationStore.notifications.slice(0, 5)
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-600 mt-1">Bienvenido, {{ authStore.userName }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <BaseCard padding="md">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center shrink-0">
              <IconStar class="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p class="text-sm text-gray-500">Puntos</p>
              <p class="text-xl font-bold text-gray-900">{{ formatPoints(authStore.userPoints) }}</p>
            </div>
          </div>
        </BaseCard>

        <BaseCard padding="md">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <IconReport class="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p class="text-sm text-gray-500">Mis reportes</p>
              <p class="text-xl font-bold text-gray-900">{{ reportStore.total }}</p>
            </div>
          </div>
        </BaseCard>

        <BaseCard padding="md">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shrink-0">
              <IconReport class="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p class="text-sm text-gray-500">Resueltos</p>
              <p class="text-xl font-bold text-gray-900">{{ reportStore.resolvedCount }}</p>
            </div>
          </div>
        </BaseCard>

        <BaseCard padding="md">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
              <IconBell class="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p class="text-sm text-gray-500">No leídas</p>
              <p class="text-xl font-bold text-gray-900">{{ notificationStore.unreadCount }}</p>
            </div>
          </div>
        </BaseCard>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BaseCard>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Últimos reportes</h2>
            <router-link to="/reports" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              Ver todos
            </router-link>
          </div>
          <div v-if="reportStore.loading" class="py-8">
            <BaseSpinner size="sm" text="" />
          </div>
          <div v-else-if="reportStore.reports.length === 0" class="text-center py-8 text-gray-500">
            <p>Aún no tienes reportes</p>
            <router-link to="/reports/create" class="text-emerald-600 hover:text-emerald-700 font-medium text-sm mt-2 inline-block">
              Crear tu primer reporte
            </router-link>
          </div>
          <div v-else class="space-y-3">
            <router-link
              v-for="report in reportStore.reports.slice(0, 5)"
              :key="report.id"
              :to="`/reports/${report.id}`"
              class="block p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ report.title }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ formatDate(report.created_at) }}</p>
                </div>
                <BaseBadge :variant="report.status === 'resolved' ? 'success' : report.status === 'pending' ? 'warning' : report.status === 'in_progress' ? 'info' : 'danger'" size="sm">
                  {{ getStatusLabel(report.status) }}
                </BaseBadge>
              </div>
            </router-link>
          </div>
        </BaseCard>

        <BaseCard>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Notificaciones recientes</h2>
            <router-link to="/notifications" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              Ver todas
            </router-link>
          </div>
          <div v-if="recentNotifications.length === 0" class="text-center py-8 text-gray-500">
            <p>Sin notificaciones</p>
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
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <router-link
          to="/reports/create"
          class="flex items-center justify-center gap-2 p-4 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors font-medium"
        >
          <span>+</span>
          Nuevo reporte
        </router-link>
        <router-link
          to="/rewards"
          class="flex items-center justify-center gap-2 p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
        >
          <IconGift class="w-5 h-5" />
          Canjear puntos
        </router-link>
        <router-link
          to="/profile"
          class="flex items-center justify-center gap-2 p-4 bg-gray-700 text-white rounded-xl hover:bg-gray-800 transition-colors font-medium"
        >
          <IconUser class="w-5 h-5" />
          Mi perfil
        </router-link>
      </div>
    </div>
  </AppLayout>
</template>
