<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useReportStore } from '../stores/reportStore'
import { useNotificationStore } from '../stores/notificationStore'
import { reportsApi } from '../api/reports'
import { formatPoints, getStatusLabel, formatDate } from '../utils/format'
import type { Report } from '../types'
import type { MapMarkerData } from '../components/maps/MapMarker'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import MapView from '../components/maps/MapView.vue'
import IconGift from '../components/icons/IconGift.vue'
import IconReport from '../components/icons/IconReport.vue'
import IconStar from '../components/icons/IconStar.vue'
import IconBell from '../components/icons/IconBell.vue'
import IconUser from '../components/icons/IconUser.vue'
import IconNotification from '../components/icons/IconNotification.vue'

const router = useRouter()
const authStore = useAuthStore()
const reportStore = useReportStore()
const notificationStore = useNotificationStore()

const availableReports = ref<Report[]>([])
const loadingAvailable = ref(false)

onMounted(async () => {
  await Promise.all([
    reportStore.fetchMyReports(),
    notificationStore.fetchNotifications(),
    fetchAvailable(),
  ])
})

async function fetchAvailable() {
  loadingAvailable.value = true
  try {
    availableReports.value = await reportsApi.list({ status: 'pending', limit: 10 })
  } catch {
    // silent
  } finally {
    loadingAvailable.value = false
  }
}

async function claimReport(report: Report) {
  try {
    const { reportsApi } = await import('../api/reports')
    await reportsApi.claim(report.id)
    availableReports.value = availableReports.value.filter(r => r.id !== report.id)
  } catch {
    // silent
  }
}

const recentNotifications = computed(() => (notificationStore.notifications || []).slice(0, 5))

const mapMarkers = computed<MapMarkerData[]>(() =>
  reportStore.reports
    .filter(r => typeof r.latitude === 'number' && typeof r.longitude === 'number')
    .map(r => ({
      id: r.id,
      position: { lat: r.latitude, lng: r.longitude },
      title: r.title,
      description: r.waste_type_name,
      icon: r.status,
    }))
)

const mapCenter = computed(() => {
  if (mapMarkers.value.length === 0) return { lat: 19.4326, lng: -99.1332 }
  return mapMarkers.value[0].position
})

function onMarkerClick(marker: MapMarkerData) {
  router.push(`/reports/${marker.id}`)
}
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
              <p class="text-sm text-gray-500">Limpiados</p>
              <p class="text-xl font-bold text-gray-900">{{ reportStore.cleanedCount }}</p>
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
            <h2 class="text-lg font-semibold text-gray-900">Tareas disponibles</h2>
            <router-link to="/reports?status=pending" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              Ver todas
            </router-link>
          </div>
          <div v-if="loadingAvailable" class="py-8">
            <BaseSpinner size="sm" text="" />
          </div>
          <div v-else-if="availableReports.length === 0" class="text-center py-12 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto mb-3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
            <p class="text-lg font-medium text-gray-500">No hay tareas disponibles</p>
            <p class="text-sm text-gray-400 mt-1">Vuelve más tarde para ver nuevos reportes</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="report in availableReports"
              :key="report.id"
              class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="min-w-0 flex-1">
                <router-link :to="`/reports/${report.id}`" class="text-sm font-medium text-gray-900 hover:text-emerald-600 truncate block">
                  {{ report.title }}
                </router-link>
                <p class="text-xs text-gray-500 mt-0.5">{{ report.waste_type_name }} - {{ formatDate(report.created_at) }}</p>
              </div>
              <BaseButton size="sm" class="shrink-0 ml-3" @click="claimReport(report)">
                Reclamar
              </BaseButton>
            </div>
          </div>
        </BaseCard>

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
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BaseCard>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900">Mis reportes</h2>
            <router-link to="/reports" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
              Ver todos
            </router-link>
          </div>
          <div v-if="reportStore.loading" class="py-8">
            <BaseSpinner size="sm" text="" />
          </div>
          <div v-else-if="reportStore.reports.length === 0" class="text-center py-12 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto mb-3">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z" />
            </svg>
            <p class="text-lg font-medium text-gray-500">Aún no tienes reportes</p>
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
                <BaseBadge :variant="report.status === 'cleaned' ? 'success' : report.status === 'pending' ? 'warning' : 'info'" size="sm">
                  {{ getStatusLabel(report.status) }}
                </BaseBadge>
              </div>
            </router-link>
          </div>
        </BaseCard>

        <BaseCard v-if="mapMarkers.length > 0">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold text-gray-900">Mapa</h2>
          </div>
          <MapView
            :center="mapCenter"
            :zoom="13"
            :markers="mapMarkers"
            :height="'300px'"
            @marker-click="onMarkerClick"
          />
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
