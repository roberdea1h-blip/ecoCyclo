<script setup lang="ts">
// Componente de mapa abstracto.
// Cuando se integre Leaflet, este componente renderizará un mapa
// OpenStreetMap usando Leaflet. Por ahora renderiza un placeholder.
//
// Uso futuro:
//   import L from 'leaflet'
//   import 'leaflet/dist/leaflet.css'
//   onMounted(() => {
//     const map = L.map('map-container').setView([props.lat, props.lng], 13)
//     L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
//     emit('ready', map)
//   })

import type { MapCoordinates, MapMarkerData } from './MapMarker'

const props = defineProps<{
  center: MapCoordinates
  zoom?: number
  markers?: MapMarkerData[]
  height?: string
}>()

defineEmits<{
  ready: [map: unknown]
  markerClick: [marker: MapMarkerData]
}>()
</script>

<template>
  <!--
    Placeholder del mapa.
    Reemplazar con <div id="map-container" :style="{ height }" />
    cuando Leaflet esté integrado.
  -->
  <div
    class="bg-gray-100 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center"
    :style="{ height: height || '300px' }"
  >
    <div class="text-center text-gray-500">
      <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
      <p class="text-sm">Mapa no disponible</p>
      <p class="text-xs mt-1">Lat: {{ center.lat }}, Lng: {{ center.lng }}</p>
      <p class="text-xs text-gray-400 mt-2">Integrar con Leaflet para activar</p>
    </div>
  </div>
</template>
