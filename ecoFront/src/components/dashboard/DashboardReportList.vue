<script setup lang="ts">
import { formatDate } from '../../utils/format'
import type { Report } from '../../types'
import BaseCard from '../base/BaseCard.vue'
import BaseSpinner from '../base/BaseSpinner.vue'

defineProps<{
  title: string
  viewAllLink: string
  loading: boolean
  reports: Report[]
  emptyMessage: string
  emptySubtext?: string
  emptyIconType?: 'check' | 'globe' | 'envelope'
}>()

const emptyIcons: Record<string, string> = {
  check: 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  globe: 'M15.59 14.37a6 6 0 0 1-5.84 7.38v-4.8m5.84-2.58a14.98 14.98 0 0 0 6.16-12.12A14.98 14.98 0 0 0 9.631 8.41m5.96 5.96a14.926 14.926 0 0 1-5.841 2.58m-.119-8.54a6 6 0 0 0-7.38 5.84h4.8m2.581-5.84a14.927 14.927 0 0 0-2.58 5.84m2.699 2.7c-.103.021-.207.041-.311.06a15.09 15.09 0 0 1-2.448-2.448 14.9 14.9 0 0 1 .06-.312m-2.24 2.39a4.493 4.493 0 0 0-1.757 4.306 4.493 4.493 0 0 0 4.306-1.758M16.5 9a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z',
  envelope: 'M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z',
}
</script>

<template>
  <BaseCard>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">{{ title }}</h2>
      <router-link :to="viewAllLink" class="text-sm text-emerald-600 hover:text-emerald-700 font-medium">
        Ver todas
      </router-link>
    </div>
    <div v-if="loading" class="py-8">
      <BaseSpinner size="sm" text="" />
    </div>
    <div v-else-if="reports.length === 0" class="text-center py-12 text-gray-400">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-16 h-16 mx-auto mb-3">
        <path stroke-linecap="round" stroke-linejoin="round" :d="emptyIcons[emptyIconType || 'check']" />
      </svg>
      <p class="text-lg font-medium text-gray-500">{{ emptyMessage }}</p>
      <p v-if="emptySubtext" class="text-sm text-gray-400 mt-1">{{ emptySubtext }}</p>
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="report in reports"
        :key="report.id"
        class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <div class="min-w-0 flex-1">
          <router-link :to="`/reports/${report.id}`" class="text-sm font-medium text-gray-900 hover:text-emerald-600 truncate block">
            {{ report.title }}
          </router-link>
          <slot name="subtitle" :report="report">
            <p class="text-xs text-gray-500 mt-0.5">{{ report.waste_type_name }} - {{ formatDate(report.created_at) }}</p>
          </slot>
        </div>
        <div v-if="$slots.actions" class="flex gap-2 shrink-0 ml-3">
          <slot name="actions" :report="report" />
        </div>
      </div>
    </div>
  </BaseCard>
</template>
