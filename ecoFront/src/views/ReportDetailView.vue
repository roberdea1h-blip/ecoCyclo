<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { useAuthStore } from '../stores/authStore'
import { getStatusLabel, formatDate } from '../utils/format'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import MapView from '../components/maps/MapView.vue'

const route = useRoute()
const router = useRouter()
const reportStore = useReportStore()
const authStore = useAuthStore()

const showEditModal = ref(false)
const editStatus = ref('')
const deleting = ref(false)

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'resolved', label: 'Resuelto' },
  { value: 'rejected', label: 'Rechazado' },
]

onMounted(async () => {
  const id = Number(route.params.id)
  if (isNaN(id)) {
    router.push('/reports')
    return
  }
  await reportStore.fetchReport(id)
})

const report = reportStore.currentReport
const isOwner = () => report.value?.user_id === authStore.user?.id

async function handleDelete() {
  if (!report.value || !confirm('¿Eliminar este reporte?')) return
  deleting.value = true
  try {
    await reportStore.deleteReport(report.value.id)
    router.push('/reports')
  } catch {
    deleting.value = false
  }
}

function openEdit() {
  editStatus.value = report.value?.status || 'pending'
  showEditModal.value = true
}

async function handleEdit() {
  if (!report.value) return
  await reportStore.updateReport(report.value.id, { status: editStatus.value })
  showEditModal.value = false
}
</script>

<template>
  <AppLayout>
    <div class="max-w-3xl mx-auto">
      <BaseSpinner v-if="reportStore.loading && !report" size="md" />

      <div v-else-if="!report" class="text-center py-12">
        <p class="text-gray-500">Reporte no encontrado</p>
        <router-link to="/reports" class="text-emerald-600 hover:text-emerald-700 font-medium mt-2 inline-block">
          Volver a reportes
        </router-link>
      </div>

      <template v-else>
        <div class="flex items-center justify-between mb-6">
          <div>
            <router-link to="/reports" class="text-sm text-gray-500 hover:text-gray-700 mb-2 inline-block">
              &larr; Volver
            </router-link>
            <h1 class="text-2xl font-bold text-gray-900">{{ report.title }}</h1>
          </div>
          <div class="flex items-center gap-2">
            <BaseBadge
              :variant="report.status === 'resolved' ? 'success' : report.status === 'pending' ? 'warning' : report.status === 'in_progress' ? 'info' : 'danger'"
              size="md"
            >
              {{ getStatusLabel(report.status) }}
            </BaseBadge>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div class="lg:col-span-2 space-y-6">
            <BaseCard>
              <div class="space-y-4">
                <div>
                  <h3 class="text-sm font-medium text-gray-500">Descripción</h3>
                  <p class="mt-1 text-gray-900">{{ report.description }}</p>
                </div>
                <div v-if="report.address">
                  <h3 class="text-sm font-medium text-gray-500">Dirección</h3>
                  <p class="mt-1 text-gray-900">{{ report.address }}</p>
                </div>
                <div v-if="report.image_url">
                  <h3 class="text-sm font-medium text-gray-500 mb-2">Imagen</h3>
                  <img :src="report.image_url" alt="Report" class="rounded-lg w-full max-w-md" />
                </div>
              </div>
            </BaseCard>

            <BaseCard>
              <h3 class="text-sm font-medium text-gray-500 mb-3">Ubicación</h3>
              <MapView
                :center="{ lat: report.latitude, lng: report.longitude }"
                :zoom="15"
                :height="'300px'"
              />
            </BaseCard>
          </div>

          <div class="space-y-4">
            <BaseCard padding="sm">
              <div class="space-y-3 text-sm">
                <div>
                  <span class="text-gray-500">Reportado por:</span>
                  <p class="font-medium text-gray-900">{{ report.user_name }}</p>
                </div>
                <div>
                  <span class="text-gray-500">Tipo:</span>
                  <p class="font-medium text-gray-900">{{ report.waste_type_name }}</p>
                </div>
                <div>
                  <span class="text-gray-500">Creado:</span>
                  <p class="font-medium text-gray-900">{{ formatDate(report.created_at) }}</p>
                </div>
                <div v-if="report.updated_at !== report.created_at">
                  <span class="text-gray-500">Actualizado:</span>
                  <p class="font-medium text-gray-900">{{ formatDate(report.updated_at) }}</p>
                </div>
              </div>
            </BaseCard>

            <div v-if="isOwner()" class="space-y-2">
              <BaseButton variant="secondary" class="w-full" @click="openEdit">
                Cambiar estado
              </BaseButton>
              <BaseButton variant="danger" class="w-full" :loading="deleting" @click="handleDelete">
                Eliminar
              </BaseButton>
            </div>
          </div>
        </div>
      </template>
    </div>

    <BaseModal v-model="showEditModal" title="Cambiar estado">
      <div class="space-y-4">
        <BaseSelect
          v-model="editStatus"
          label="Nuevo estado"
          :options="statusOptions"
        />
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showEditModal = false">Cancelar</BaseButton>
        <BaseButton :loading="reportStore.loading" @click="handleEdit">Guardar</BaseButton>
      </template>
    </BaseModal>
  </AppLayout>
</template>
