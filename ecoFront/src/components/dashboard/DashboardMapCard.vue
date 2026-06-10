<script setup lang="ts">
import type { MapMarkerData } from '../../types'
import BaseCard from '../base/BaseCard.vue'
import MapView from '../maps/MapView.vue'

defineProps<{
  center: { lat: number; lng: number }
  markers: MapMarkerData[]
}>()

defineEmits<{
  'marker-click': [marker: MapMarkerData]
}>()
</script>

<template>
  <BaseCard>
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-semibold text-gray-900">Mapa</h2>
    </div>
    <MapView
      :center="center"
      :zoom="13"
      :markers="markers"
      :height="'300px'"
      @marker-click="(m: MapMarkerData) => $emit('marker-click', m)"
    />
  </BaseCard>
</template>
