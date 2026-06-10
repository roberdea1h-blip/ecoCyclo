<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { wasteTypesApi } from '../api/wasteTypes'
import { getStatusLabel, getStatusColor, formatDate } from '../utils/format'
import type { WasteType } from '../types'
import type { MapMarkerData } from '../components/maps/MapMarker'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import MapView from '../components/maps/MapView.vue'

const router = useRouter()
const reportStore = useReportStore()
const wasteTypes = ref<WasteType[]>([])
const currentPage = ref(1)
const showMap = ref(false)

const mapMarkers = computed<MapMarkerData[]>(() =>
  reportStore.reports
    .filter(r => typeof r.latitude === 'number' && typeof r.longitude === 'number')
    .map(r => ({
      id: r.id,
      position: { lat: r.latitude, lng: r.longitude },
      title: r.title,
      description: r.waste_type_name,
      icon: r.status,
    }))
)

const mapCenter = computed(() => {
  if (mapMarkers.value.length === 0) return { lat: 19.4326, lng: -99.1332 }
  if (mapMarkers.value.length === 1) return mapMarkers.value[0].position
  const sum = mapMarkers.value.reduce(
    (acc, m) => ({ lat: acc.lat + m.position.lat, lng: acc.lng + m.position.lng }),
    { lat: 0, lng: 0 }
  )
  return { lat: sum.lat / mapMarkers.value.length, lng: sum.lng / mapMarkers.value.length }
})

function onMarkerClick(marker: MapMarkerData) {
  router.push(`/reports/${marker.id}`)
}

const statusOptions = [
  { value: '', label: 'Todos los estados' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'pending_review', label: 'Pendiente de revisión' },
  { value: 'verified', label: 'Verificado' },
  { value: 'rejected', label: 'Rechazado' },
  { value: 'cleaned', label: 'Limpiado' },
]

const wasteOptions = ref([{ value: '', label: 'Todos los tipos' }])

onMounted(async () => {
  try {
    wasteTypes.value = await wasteTypesApi.list()
    wasteTypes.value.forEach(wt => {
      wasteOptions.value.push({ value: wt.id, label: wt.name })
    })
  } catch {
    // ignore
  }
  await reportStore.fetchReports({ page: 1 })
})

watch([() => reportStore.filterStatus, () => reportStore.filterWasteType], () => {
  currentPage.value = 1
  reportStore.fetchReports({ page: 1 })
})

function onFilterChange() {
  reportStore.setFilter(reportStore.filterStatus, reportStore.filterWasteType)
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    reportStore.fetchReports({ page: currentPage.value })
  }
}

function nextPage() {
  if (currentPage.value < reportStore.pages) {
    currentPage.value++
    reportStore.fetchReports({ page: currentPage.value })
  }
}
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Reportes</h1>
          <p class="text-gray-600 mt-1">Reportes de puntos de acumulación</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="text-sm px-3 py-1.5 rounded-lg font-medium transition-colors"
            :class="showMap ? 'bg-gray-100 text-gray-600 hover:bg-gray-200' : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'"
            @click="showMap = false"
          >
            Lista
          </button>
          <button
            type="button"
            class="text-sm px-3 py-1.5 rounded-lg font-medium transition-colors"
            :class="showMap ? 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            @click="showMap = true"
          >
            Mapa
          </button>
          <router-link to="/reports/create">
            <BaseButton>Nuevo reporte</BaseButton>
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <BaseSelect
          v-model="reportStore.filterStatus"
          label="Estado"
          :options="statusOptions"
          @update:model-value="onFilterChange"
        />
        <BaseSelect
          v-model="reportStore.filterWasteType"
          label="Tipo de residuo"
          :options="wasteOptions"
          @update:model-value="onFilterChange"
        />
      </div>

      <template v-if="showMap">
        <div v-if="reportStore.loading" class="py-12 text-center">
          <BaseSpinner size="md" />
        </div>
        <div v-else-if="mapMarkers.length === 0" class="text-center py-12 text-gray-500">
          <p class="text-lg">No hay reportes con ubicación</p>
        </div>
        <MapView
          v-else
          :center="mapCenter"
          :zoom="12"
          :markers="mapMarkers"
          :height="'600px'"
          @marker-click="onMarkerClick"
        />
      </template>

      <template v-else>
        <BaseSpinner v-if="reportStore.loading" size="md" />

        <div v-else-if="reportStore.reports.length === 0" class="text-center py-16 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-20 h-20 mx-auto mb-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.012 1.244l.256.512a2.25 2.25 0 0 0 2.013 1.244h3.218a2.25 2.25 0 0 0 2.013-1.244l.256-.512a2.25 2.25 0 0 1 2.013-1.244h3.859m-19.5.338V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 0 0-2.15-1.588H6.911a2.25 2.25 0 0 0-2.15 1.588L2.35 13.177a2.25 2.25 0 0 0-.1.661Z" />
          </svg>
          <p class="text-xl font-medium text-gray-500">No hay reportes</p>
          <router-link to="/reports/create" class="text-emerald-600 hover:text-emerald-700 font-medium mt-2 inline-block">
            Crear el primer reporte
          </router-link>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link
            v-for="report in reportStore.reports"
            :key="report.id"
            :to="`/reports/${report.id}`"
            class="block"
          >
            <BaseCard hover class="h-full">
              <div class="space-y-3">
                <div class="flex items-start justify-between gap-2">
                  <h3 class="font-semibold text-gray-900 truncate">{{ report.title }}</h3>
                  <BaseBadge
                    size="sm"
                    :variant="report.status === 'verified' || report.status === 'cleaned' ? 'success' : report.status === 'rejected' ? 'danger' : report.status === 'pending' || report.status === 'pending_review' ? 'warning' : 'info'"
                  >
                    {{ getStatusLabel(report.status) }}
                  </BaseBadge>
                </div>
                <p class="text-sm text-gray-600 line-clamp-2">{{ report.description }}</p>
                <div class="flex items-center justify-between text-xs text-gray-400">
                  <span>{{ report.waste_type_name }}</span>
                  <span>{{ formatDate(report.created_at) }}</span>
                </div>
              </div>
            </BaseCard>
          </router-link>
        </div>

        <div v-if="reportStore.pages > 1" class="flex items-center justify-center gap-4 mt-6">
          <BaseButton :disabled="currentPage <= 1" variant="secondary" size="sm" @click="prevPage">
            Anterior
          </BaseButton>
          <span class="text-sm text-gray-600">
            Página {{ currentPage }} de {{ reportStore.pages }}
          </span>
          <BaseButton :disabled="currentPage >= reportStore.pages" variant="secondary" size="sm" @click="nextPage">
            Siguiente
          </BaseButton>
        </div>
      </template>
    </div>
  </AppLayout>
</template>
