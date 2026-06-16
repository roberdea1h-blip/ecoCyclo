<script setup lang="ts">
import { computed } from 'vue'
import type { WasteType, Report } from '../../types'
import { formatPoints } from '../../utils/format'
import BaseCard from '../base/BaseCard.vue'

const props = defineProps<{
  wasteTypes: WasteType[]
  reports?: Report[]
  compact?: boolean
}>()

const totalPoints = computed(() =>
  props.wasteTypes.reduce((sum, wt) => sum + wt.points_per_report, 0)
)

const reportCounts = computed(() => {
  if (!props.reports) return new Map<string, number>()
  const counts = new Map<string, number>()
  for (const r of props.reports) {
    counts.set(r.waste_type_id, (counts.get(r.waste_type_id) || 0) + 1)
  }
  return counts
})