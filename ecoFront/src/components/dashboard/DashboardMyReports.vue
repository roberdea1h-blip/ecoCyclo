<script setup lang="ts">
import { useReportStore } from '../../stores/reportStore'
import { getStatusLabel, formatDate } from '../../utils/format'
import BaseCard from '../base/BaseCard.vue'
import BaseBadge from '../base/BaseBadge.vue'
import BaseSpinner from '../base/BaseSpinner.vue'

const reportStore = useReportStore()
</script>

<template>
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
          <BaseBadge
            :variant="report.status === 'verified' || report.status === 'cleaned' ? 'success' : report.status === 'rejected' ? 'danger' : report.status === 'pending' || report.status === 'pending_review' ? 'warning' : 'info'"
            size="sm"
          >
            {{ getStatusLabel(report.status) }}
          </BaseBadge>
        </div>
      </router-link>
    </div>
  </BaseCard>
</template>
