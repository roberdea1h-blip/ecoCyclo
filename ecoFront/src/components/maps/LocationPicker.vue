<script setup lang="ts">
import MapView from './MapView.vue'
import type { MapCoordinates } from './MapMarker'

const props = defineProps<{
  modelValue: MapCoordinates | null
}>()

const emit = defineEmits<{
  'update:modelValue': [coords: MapCoordinates]
}>()

const defaultCenter: MapCoordinates = { lat: 19.4326, lng: -99.1332 }

function onMapClick(coords: MapCoordinates) {
  emit('update:modelValue', coords)
}

function useCurrentLocation() {
  if (!navigator.geolocation) {
    alert('Geolocalización no soportada')
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const coords = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      emit('update:modelValue', coords)
    },
    () => {
      emit('update:modelValue', defaultCenter)
    }
  )
}
</script>

<template>
  <div class="space-y-2">
    <MapView
      :center="modelValue || defaultCenter"
      :zoom="15"
      :height="'250px'"
      :clickable="true"
      @map-click="onMapClick"
    />
    <div class="flex items-center justify-between">
      <button
        type="button"
        class="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
        @click="useCurrentLocation"
      >
        Usar mi ubicación actual
      </button>
      <p v-if="modelValue" class="text-xs text-gray-500">
        {{ modelValue.lat.toFixed(6) }}, {{ modelValue.lng.toFixed(6) }}
      </p>
      <p v-else class="text-xs text-gray-400">Haz clic en el mapa para seleccionar</p>
    </div>
  </div>
</template>
