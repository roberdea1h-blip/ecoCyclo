<script setup lang="ts">
import { computed } from 'vue'
import { useReportStore } from '../../stores/reportStore'
import { getStatusLabel, getStatusColor, formatDate } from '../../utils/format'
import type { Report } from '../../types'
import BaseCard from '../base/BaseCard.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseBadge from '../base/BaseBadge.vue'

const reportStore = useReportStore()

const emit = defineEmits<{
  revoke: [report: Report]
  verify: [report: Report]
  reject: [report: Report]
}>()

const activeReports = computed(() =>
  reportStore.reports.filter(r => r.status === 'in_progress' || r.status === 'pending_review')
)

const inProgress = computed(() =>
  activeReports.value.filter(r => r.status === 'in_progress')
)

const pendingReview = computed(() =>
  activeReports.value.filter(r => r.status === 'pending_review')
)

const hasAny = computed(() => activeReports.value.length > 0)

function getBadgeVariant(status: string) {
  if (status === 'in_progress') return 'info'
  if (status === 'pending_review') return 'warning'
  return 'default'
}
</script>

<template>
  <BaseCard>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">Mis reportes activos</h2>
      <router-link to="/reports/mine" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
        Ver todos
      </router-link>
    </div>

    <div v-if="!hasAny" class="text-center py-12 text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto mb-3">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
      <p class="text-lg font-medium text-gray-500">No tienes reportes activos</p>
      <p class="text-sm text-gray-400 mt-1">Los reportes reclamados o pendientes de revisión aparecerán aquí</p>
    </div>

    <div v-else class="space-y-6">
      <div v-if="inProgress.length > 0">
        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">En progreso</h3>
        <div class="space-y-3">
          <div
            v-for="report in inProgress"
            :key="report.id"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="min-w-0 flex-1">
              <router-link
                :to="`/reports/${report.id}`"
                class="text-sm font-medium text-gray-900 hover:text-emerald-600 truncate block"
              >
                {{ report.title }}
              </router-link>
              <p class="text-xs text-gray-500 mt-0.5">
                Asignado a: <span class="font-medium">{{ report.cleaner_name || 'Voluntario' }}</span>
                <span class="mx-1">&middot;</span>
                {{ formatDate(report.created_at) }}
              </p>
            </div>
            <div class="flex gap-2 shrink-0 ml-3">
              <BaseButton size="sm" variant="danger" @click="emit('revoke', report)">Revocar asignación</BaseButton>
            </div>
          </div>
        </div>
      </div>

      <div v-if="pendingReview.length > 0">
        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Pendientes de revisión</h3>
        <div class="space-y-3">
          <div
            v-for="report in pendingReview"
            :key="report.id"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="min-w-0 flex-1">
              <router-link
                :to="`/reports/${report.id}`"
                class="text-sm font-medium text-gray-900 hover:text-emerald-600 truncate block"
              >
                {{ report.title }}
              </router-link>
              <p class="text-xs text-gray-500 mt-0.5">
                Completado por: <span class="font-medium">{{ report.cleaner_name || 'Voluntario' }}</span>
                <span class="mx-1">&middot;</span>
                {{ formatDate(report.cleaned_at || report.created_at) }}
              </p>
            </div>
            <div class="flex gap-2 shrink-0 ml-3">
              <BaseButton size="sm" variant="primary" @click="emit('verify', report)">Verificar limpieza</BaseButton>
              <BaseButton size="sm" variant="danger" @click="emit('reject', report)">Rechazar limpieza</BaseButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseCard>
</template>
