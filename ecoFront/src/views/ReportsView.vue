<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useReportStore } from '../stores/reportStore'
import { wasteTypesApi } from '../api/wasteTypes'
import { getStatusLabel, getStatusColor, formatDate } from '../utils/format'
import type { WasteType } from '../types'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSelect from '../components/base/BaseSelect.vue'

const reportStore = useReportStore()
const wasteTypes = ref<WasteType[]>([])
const currentPage = ref(1)

const statusOptions = [
  { value: '', label: 'Todos los estados' },
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'resolved', label: 'Resuelto' },
  { value: 'rejected', label: 'Rechazado' },
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
        <router-link to="/reports/create">
          <BaseButton>Nuevo reporte</BaseButton>
        </router-link>
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

      <BaseSpinner v-if="reportStore.loading" size="md" />

      <div v-else-if="reportStore.reports.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-lg">No hay reportes</p>
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
                  :variant="report.status === 'resolved' ? 'success' : report.status === 'pending' ? 'warning' : report.status === 'in_progress' ? 'info' : 'danger'"
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
    </div>
  </AppLayout>
</template>
