<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { MapCoordinates, MapMarkerData } from './MapMarker'

const props = withDefaults(defineProps<{
  center: MapCoordinates
  zoom?: number
  markers?: MapMarkerData[]
  height?: string
  clickable?: boolean
}>(), {
  zoom: 13,
  height: '300px',
  clickable: false,
})

const emit = defineEmits<{
  ready: [map: L.Map]
  markerClick: [marker: MapMarkerData]
  mapClick: [coords: MapCoordinates]
}>()

const mapContainer = ref<HTMLDivElement>()
let map: L.Map | null = null
let markerLayer: L.LayerGroup | null = null
let selectedMarker: L.CircleMarker | null = null

const statusColors: Record<string, string> = {
  pending: '#f59e0b',
  in_progress: '#3b82f6',
  cleaned: '#10b981',
  default: '#6b7280',
}

function getStatusColor(status?: string): string {
  return statusColors[status || 'default'] || statusColors.default
}

function createStatusIcon(marker: MapMarkerData): L.DivIcon {
  const color = marker.color || getStatusColor(marker.icon)
  return L.divIcon({
    className: '',
    html: `<div style="width:22px;height:22px;background:${color};border:3px solid #fff;border-radius:50%;box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  })
}

function buildPinSvg(color: string): string {
  const pin = encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="40" viewBox="0 0 28 40">
      <path d="M14 0C6.3 0 0 6.3 0 14c0 10.5 14 26 14 26s14-15.5 14-26C28 6.3 21.7 0 14 0z" fill="${color}" stroke="#fff" stroke-width="2"/>
      <circle cx="14" cy="14" r="5" fill="#fff"/>
    </svg>`
  )
  return `data:image/svg+xml;charset=utf-8,${pin}`
}

function addMarkers(markers: MapMarkerData[]) {
  if (!map) return
  if (markerLayer) markerLayer.clearLayers()
  else markerLayer = L.layerGroup().addTo(map)

  markers.forEach(marker => {
    const lMarker = L.marker([marker.position.lat, marker.position.lng], {
      icon: createStatusIcon(marker),
    })

    if (marker.title || marker.description) {
      lMarker.bindPopup(
        `<div style="font-family:system-ui,sans-serif;font-size:13px">
          ${marker.title ? `<b>${marker.title}</b>` : ''}
          ${marker.description ? `<br><span style="color:#666">${marker.description}</span>` : ''}
        </div>`
      )
    }

    lMarker.on('click', () => emit('markerClick', marker))
    markerLayer?.addLayer(lMarker)
  })
}

function setView(coords: MapCoordinates, zoom?: number) {
  if (map) map.setView([coords.lat, coords.lng], zoom || props.zoom)
}

function placeSelectedMarker(coords: MapCoordinates) {
  if (!map) return
  if (selectedMarker) map.removeLayer(selectedMarker)
  selectedMarker = L.circleMarker([coords.lat, coords.lng], {
    radius: 8,
    fillColor: '#059669',
    color: '#fff',
    weight: 3,
    fillOpacity: 1,
  }).addTo(map)
  selectedMarker.bindPopup('Ubicación seleccionada').openPopup()
}

function clearSelectedMarker() {
  if (selectedMarker && map) {
    map.removeLayer(selectedMarker)
    selectedMarker = null
  }
}

onMounted(() => {
  if (!mapContainer.value) return

  map = L.map(mapContainer.value, {
    center: [props.center.lat, props.center.lng],
    zoom: props.zoom,
    zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map)

  if (props.clickable) {
    map.on('click', (e: L.LeafletMouseEvent) => {
      const coords = { lat: e.latlng.lat, lng: e.latlng.lng }
      placeSelectedMarker(coords)
      emit('mapClick', coords)
    })
  }

  if (props.markers?.length) {
    addMarkers(props.markers)
    if (props.markers.length === 1) {
      const m = props.markers[0]
      map.setView([m.position.lat, m.position.lng], props.zoom > 13 ? props.zoom : 14)
    }
  }

  emit('ready', map)
})

watch(() => props.center, (coords) => {
  setView(coords)
})

watch(() => props.markers, (markers) => {
  if (markers?.length) addMarkers(markers)
}, { deep: true })

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

defineExpose({ setView, placeSelectedMarker, clearSelectedMarker })
</script>

<template>
  <div ref="mapContainer" class="rounded-xl overflow-hidden" :style="{ height, isolation: 'isolate' }" />
</template>
