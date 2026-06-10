<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useReportStore } from '../stores/reportStore'
import { useNotificationStore } from '../stores/notificationStore'
import { reportsApi } from '../api/reports'
import { formatDate } from '../utils/format'
import { useApiError } from '../composables/useApiError'
import type { Report } from '../types'
import type { MapMarkerData } from '../components/maps/MapMarker'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseButton from '../components/base/BaseButton.vue'

import DashboardStatsCards from '../components/dashboard/DashboardStatsCards.vue'
import DashboardReportList from '../components/dashboard/DashboardReportList.vue'
import DashboardNotificationsList from '../components/dashboard/DashboardNotificationsList.vue'
import DashboardMyReports from '../components/dashboard/DashboardMyReports.vue'
import DashboardMapCard from '../components/dashboard/DashboardMapCard.vue'
import DashboardQuickActions from '../components/dashboard/DashboardQuickActions.vue'
import DashboardCompleteModal from '../components/dashboard/DashboardCompleteModal.vue'
import DashboardRejectModal from '../components/dashboard/DashboardRejectModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const reportStore = useReportStore()
const notificationStore = useNotificationStore()
const { handleError } = useApiError()
const dashboardError = ref<string | null>(null)

const availableReports = ref<Report[]>([])
const loadingAvailable = ref(false)
const claimedReports = ref<Report[]>([])
const loadingClaimed = ref(false)
const pendingReviewReports = ref<Report[]>([])
const loadingPendingReview = ref(false)

const showCompleteModal = ref(false)
const completeTarget = ref<Report | null>(null)

const showRejectModal = ref(false)
const rejectTarget = ref<Report | null>(null)

onMounted(async () => {
  await Promise.all([
    reportStore.fetchMyReports(),
    notificationStore.fetchNotifications(),
    fetchAvailable(),
    fetchClaimed(),
    fetchPendingReview(),
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

async function fetchClaimed() {
  loadingClaimed.value = true
  try {
    claimedReports.value = await reportsApi.claimed({ limit: 10 })
  } catch {
    // silent
  } finally {
    loadingClaimed.value = false
  }
}

async function fetchPendingReview() {
  loadingPendingReview.value = true
  try {
    pendingReviewReports.value = await reportsApi.pendingReview({ limit: 10 })
  } catch {
    // silent
  } finally {
    loadingPendingReview.value = false
  }
}

async function claimReport(report: Report) {
  try {
    await reportsApi.claim(report.id)
    availableReports.value = availableReports.value.filter(r => r.id !== report.id)
  } catch {
    // silent
  }
}

function openComplete(report: Report) {
  completeTarget.value = report
  showCompleteModal.value = true
}

async function handleComplete(data: { collected_weight?: number; notes?: string }) {
  if (!completeTarget.value) return
  try {
    await reportsApi.complete(completeTarget.value.id, data)
    claimedReports.value = claimedReports.value.filter(r => r.id !== completeTarget.value!.id)
    showCompleteModal.value = false
  } catch {
    // silent
  }
}

async function handleUnclaim(report: Report) {
  if (!confirm('¿Liberar esta tarea? El reporte volverá a estado pendiente.')) return
  try {
    await reportsApi.unclaim(report.id)
    claimedReports.value = claimedReports.value.filter(r => r.id !== report.id)
    availableReports.value.unshift(report)
  } catch {
    // silent
  }
}

function openReject(report: Report) {
  rejectTarget.value = report
  showRejectModal.value = true
}

async function handleVerify(report: Report) {
  try {
    await reportsApi.verify(report.id)
    pendingReviewReports.value = pendingReviewReports.value.filter(r => r.id !== report.id)
  } catch {
    // silent
  }
}

async function handleReject(data: { reason?: string }) {
  if (!rejectTarget.value) return
  try {
    await reportsApi.reject(rejectTarget.value.id, data)
    pendingReviewReports.value = pendingReviewReports.value.filter(r => r.id !== rejectTarget.value!.id)
    showRejectModal.value = false
  } catch {
    // silent
  }
}

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

      <DashboardStatsCards
        :points="authStore.userPoints"
        :total-reports="reportStore.total"
        :verified="reportStore.cleanedCount + reportStore.verifiedCount"
        :unread-count="notificationStore.unreadCount"
      />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardReportList
          title="Tareas disponibles"
          view-all-link="/reports?status=pending"
          :loading="loadingAvailable"
          :reports="availableReports"
          empty-message="No hay tareas disponibles"
          empty-subtext="Vuelve más tarde para ver nuevos reportes"
        >
          <template #actions="{ report }">
            <BaseButton size="sm" @click="claimReport(report)">Reclamar</BaseButton>
          </template>
        </DashboardReportList>

        <DashboardReportList
          title="Mis tareas activas"
          view-all-link="/reports?status=in_progress"
          :loading="loadingClaimed"
          :reports="claimedReports"
          empty-message="No tienes tareas activas"
          empty-subtext="Reclama una tarea disponible para comenzar"
          empty-icon-type="globe"
        >
          <template #actions="{ report }">
            <BaseButton size="sm" variant="primary" @click="openComplete(report)">Completar</BaseButton>
            <BaseButton size="sm" variant="secondary" @click="handleUnclaim(report)">Liberar</BaseButton>
          </template>
        </DashboardReportList>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardReportList
          title="Pendientes de revisión"
          view-all-link="/reports?status=pending_review"
          :loading="loadingPendingReview"
          :reports="pendingReviewReports"
          empty-message="No hay reportes pendientes de revisión"
          empty-subtext="Los reportes marcados como limpiados aparecerán aquí"
        >
          <template #subtitle="{ report }">
            <p class="text-xs text-gray-500 mt-0.5">
              {{ report.cleaner_name ? `Limpiado por: ${report.cleaner_name}` : '' }} - {{ formatDate(report.cleaned_at || report.created_at) }}
            </p>
          </template>
          <template #actions="{ report }">
            <BaseButton size="sm" variant="primary" @click="handleVerify(report)">Verificar</BaseButton>
            <BaseButton size="sm" variant="danger" @click="openReject(report)">Rechazar</BaseButton>
          </template>
        </DashboardReportList>

        <DashboardNotificationsList />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DashboardMyReports />
        <DashboardMapCard
          v-if="mapMarkers.length > 0"
          :center="mapCenter"
          :markers="mapMarkers"
          @marker-click="onMarkerClick"
        />
      </div>

      <DashboardQuickActions />
    </div>

    <DashboardCompleteModal
      v-model:show="showCompleteModal"
      :report="completeTarget"
      @confirm="handleComplete"
    />

    <DashboardRejectModal
      v-model:show="showRejectModal"
      :report="rejectTarget"
      @confirm="handleReject"
    />
  </AppLayout>
</template>
