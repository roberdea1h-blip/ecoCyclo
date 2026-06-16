<script setup lang="ts">
import { computed } from 'vue'
import type { WasteType, Report } from '../../types'
import BaseCard from '../base/BaseCard.vue'

const props = defineProps<{
  wasteTypes: WasteType[]
  reports?: Report[]
  compact?: boolean
}>()

const reportCounts = computed(() => {
  if (!props.reports) return new Map<string, number>()
  const counts = new Map<string, number>()
  for (const r of props.reports) {
    counts.set(r.waste_type_id, (counts.get(r.waste_type_id) || 0) + 1)
  }
  return counts
})

const totalReports = computed(() => props.reports?.length ?? 0)
</script>

<template>
  <BaseCard :padding="compact ? 'sm' : 'md'">
    <h2
      class="font-semibold text-gray-900"
      :class="compact ? 'text-sm mb-2' : 'text-lg mb-3'"
    >
      Tipos de residuo
    </h2>
    <div class="space-y-1">
      <div
        v-for="wt in wasteTypes"
        :key="wt.id"
        class="flex items-center justify-between rounded-lg transition-colors"
        :class="compact ? 'px-1.5 py-1 text-xs' : 'px-2 py-1.5 text-sm hover:bg-gray-50'"
      >
        <div class="flex items-center gap-2 min-w-0">
          <span v-if="wt.icon" class="shrink-0">{{ wt.icon }}</span>
          <span class="font-medium text-gray-800 truncate">{{ wt.name }}</span>
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <span class="text-emerald-600 font-semibold whitespace-nowrap">{{ wt.points_per_kilo }} pts/kg</span>
          <span
            v-if="reportCounts.size > 0"
            class="text-gray-400 text-xs tabular-nums"
          >
            {{ reportCounts.get(wt.id) || 0 }}
          </span>
        </div>
      </div>
    </div>
    <div
      v-if="reportCounts.size > 0"
      class="border-t border-gray-100 flex justify-end font-semibold text-gray-800"
      :class="compact ? 'pt-1.5 mt-1.5 text-xs' : 'pt-2.5 mt-2.5 text-sm'"
    >
      <span class="tabular-nums">{{ totalReports }} reportes</span>
    </div>
  </BaseCard>
</template>
