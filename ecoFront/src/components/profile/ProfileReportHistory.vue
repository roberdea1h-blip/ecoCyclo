<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { reportsApi } from '../../api/reports'
import { getStatusLabel, formatDate } from '../../utils/format'
import type { Report } from '../../types'
import BaseCard from '../base/BaseCard.vue'
import BaseBadge from '../base/BaseBadge.vue'
import BaseSpinner from '../base/BaseSpinner.vue'

const loading = ref(false)
const reports = ref<(Report & { role: 'creator' | 'cleaner' })[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const [mine, claimed] = await Promise.all([
      reportsApi.mine({ limit: 100 }),
      reportsApi.claimed({ limit: 100 }),
    ])

    const seen = new Set<string>()
    const merged: (Report & { role: 'creator' | 'cleaner' })[] = []

    for (const r of mine) {
      seen.add(r.id)
      merged.push({ ...r, role: 'creator' })
    }

    for (const r of claimed) {
      if (!seen.has(r.id)) {
        merged.push({ ...r, role: 'cleaner' })
      }
    }

    merged.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    reports.value = merged
  } finally {
    loading.value = false
  }
})

function badgeVariant(status: string) {
  if (status === 'verified' || status === 'cleaned') return 'success'
  if (status === 'rejected') return 'danger'
  return 'default'
}
</script>

<template>
  <BaseCard>
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Historial de reportes</h2>
    <BaseSpinner v-if="loading" size="sm" />
    <div v-else-if="reports.length === 0" class="text-center py-8 text-gray-500">
      <p>Aún no tienes reportes</p>
    </div>
    <div v-else class="space-y-2">
      <div
        v-for="report in reports"
        :key="report.id"
        class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
      >
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <router-link
              :to="`/reports/${report.id}`"
              class="text-sm font-medium text-gray-900 hover:text-emerald-600 truncate"
            >
              {{ report.title }}
            </router-link>
            <BaseBadge
              :variant="report.role === 'creator' ? 'info' : 'success'"
              size="sm"
            >
              {{ report.role === 'creator' ? 'Creado' : 'Limpiado' }}
            </BaseBadge>
          </div>
          <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(report.created_at) }}</p>
        </div>
        <BaseBadge :variant="badgeVariant(report.status)" size="sm" class="shrink-0 ml-3">
          {{ getStatusLabel(report.status) }}
        </BaseBadge>
      </div>
    </div>
  </BaseCard>
</template>
