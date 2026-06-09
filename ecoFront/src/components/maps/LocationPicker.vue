<script setup lang="ts">
// Componente para seleccionar ubicación en el mapa.
// Cuando se integre Leaflet, permitirá al usuario hacer clic
// en el mapa para seleccionar coordenadas.
//
// Uso futuro:
//   map.on('click', (e: L.LeafletMouseEvent) => {
//     emit('select', { lat: e.latlng.lat, lng: e.latlng.lng })
//   })

import MapView from './MapView.vue'
import type { MapCoordinates } from './MapMarker'

const props = defineProps<{
  modelValue: MapCoordinates | null
}>()

const emit = defineEmits<{
  'update:modelValue': [coords: MapCoordinates]
}>()

function useCurrentLocation() {
  if (!navigator.geolocation) {
    alert('Geolocalización no soportada')
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      emit('update:modelValue', {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
      })
    },
    () => {
      // Usar coordenadas por defecto si la geolocalización falla
      emit('update:modelValue', { lat: 19.4326, lng: -99.1332 })
    }
  )
}
</script>

<template>
  <div class="space-y-2">
    <MapView
      v-if="modelValue"
      :center="modelValue"
      :zoom="15"
      :height="'250px'"
    />
    <div v-else class="bg-gray-100 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center" style="height: 250px">
      <p class="text-sm text-gray-500">Selecciona una ubicación</p>
    </div>
    <button
      type="button"
      class="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
      @click="useCurrentLocation"
    >
      Usar mi ubicación actual
    </button>
    <p v-if="modelValue" class="text-xs text-gray-500">
      Lat: {{ modelValue.lat.toFixed(6) }}, Lng: {{ modelValue.lng.toFixed(6) }}
    </p>
  </div>
</template>
