<script setup lang="ts">
import { onMounted, watch, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { useAuthStore } from '../stores/authStore'
import { getStatusLabel, formatDate, resolveImageUrl } from '../utils/format'
import type { MapMarkerData } from '../components/maps/MapMarker'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import ReportEditModal from '../components/modals/ReportEditModal.vue'
import ReportCompleteModal from '../components/modals/ReportCompleteModal.vue'
import ReportRejectModal from '../components/modals/ReportRejectModal.vue'
import ReportUnclaimModal from '../components/modals/ReportUnclaimModal.vue'
import MapView from '../components/maps/MapView.vue'

const route = useRoute()
const router = useRouter()
const reportStore = useReportStore()
const authStore = useAuthStore()

const isFetching = ref(true)

const deleting = ref(false)
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const uploadingImage = ref(false)

const showEditModal = ref(false)
const showCompleteModal = ref(false)
const showRejectModal = ref(false)
const showUnclaimModal = ref(false)

function openEdit() { showEditModal.value = true }
function openComplete() { showCompleteModal.value = true }
function openReject() { showRejectModal.value = true }
function openUnclaim() { showUnclaimModal.value = true }

async function loadReport(id: string) {
  if (!id) {
    router.push('/reports')
    return
  }
  isFetching.value = true
  await reportStore.fetchReport(id)
  isFetching.value = false
}

onMounted(() => loadReport(route.params.id as string))

watch(() => route.params.id, (newId) => {
  if (newId) loadReport(newId as string)
})
const report = computed(() => reportStore.currentReport)

const isOwner = () => report.value?.user_id === authStore.user?.id
const isCleaner = () => report.value?.cleaner_id === authStore.user?.id
const canClaim = computed(() => report.value?.status === 'pending' && !isOwner())
const canComplete = computed(() => report.value?.status === 'in_progress' && isCleaner())
const canUnclaim = computed(() => report.value?.status === 'in_progress' && isCleaner())
const canVerify = computed(() => report.value?.status === 'pending_review' && isOwner())
const canReject = computed(() => report.value?.status === 'pending_review' && isOwner())

const reportMarker = computed<MapMarkerData[]>(() => {
  const r = report.value
  if (!r || typeof r.latitude !== 'number' || typeof r.longitude !== 'number') return []
  return [{
    id: r.id,
    position: { lat: r.latitude, lng: r.longitude },
    title: r.title,
    description: r.waste_type_name || '',
    icon: r.status,
  }]
})

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

async function handleClaim() {
  if (!report.value) return
  try {
    await reportStore.claimReport(report.value.id)
  } catch {
    // handled by store
  }
}

function handleComplete(data: { collected_weight?: number; notes?: string }) {
  if (!report.value) return
  reportStore.completeReport(report.value.id, data)
}

function handleUnclaim() {
  if (!report.value) return
  reportStore.unclaimReport(report.value.id)
}

async function handleVerify() {
  if (!report.value) return
  try {
    await reportStore.verifyReport(report.value.id)
  } catch {
    // handled by store
  }
}

function handleReject(data: { reason?: string }) {
  if (!report.value) return
  reportStore.rejectReport(report.value.id, data.reason)
}

function handleEdit(data: Record<string, unknown>) {
  if (!report.value) return
  reportStore.updateReport(report.value.id, data)
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    imageFile.value = target.files[0]
    imagePreview.value = URL.createObjectURL(target.files[0])
  }
}

function clearImage() {
  imageFile.value = null
  imagePreview.value = null
}

async function handleUploadImage() {
  if (!report.value || !imageFile.value) return
  uploadingImage.value = true
  try {
    const { reportsApi } = await import('../api/reports')
    await reportsApi.uploadImage(report.value.id, imageFile.value, true)
    imageFile.value = null
    imagePreview.value = null
    await reportStore.fetchReport(report.value.id)
  } catch {
    // handled by store
  } finally {
    uploadingImage.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="max-w-3xl mx-auto">
      <div v-if="!report">
        <BaseSpinner v-if="isFetching || reportStore.loading" size="md" />
        <div v-else class="text-center py-12">
          <p class="text-gray-500">Reporte no encontrado</p>
          <router-link to="/reports" class="text-emerald-600 hover:text-emerald-700 font-medium mt-2 inline-block">
            Volver a reportes
          </router-link>
        </div>
      </div>

      <template v-else>
        <BaseAlert v-if="reportStore.error" variant="error" class="mb-4" dismissible @dismiss="reportStore.error = null">
          {{ reportStore.error }}
        </BaseAlert>
        <div class="flex items-center justify-between mb-6">
          <div>
            <router-link to="/reports" class="text-sm text-gray-500 hover:text-gray-700 mb-2 inline-block">
              &larr; Volver
            </router-link>
            <h1 class="text-2xl font-bold text-gray-900">{{ report.title }}</h1>
          </div>
          <div class="flex items-center gap-2">
            <BaseBadge
              :variant="report.status === 'verified' || report.status === 'cleaned' ? 'success' : report.status === 'rejected' ? 'danger' : report.status === 'pending_review' ? 'warning' : report.status === 'pending' ? 'warning' : 'info'"
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
                <div>
                  <h3 class="text-sm font-medium text-gray-500 mb-2">Imágenes</h3>
                  <div v-if="report.image_url" class="mb-3">
                    <img :src="resolveImageUrl(report.image_url)" alt="Report" class="rounded-lg w-full max-w-md" />
                  </div>
                  <div v-if="isOwner() && report.status === 'pending'" class="border-2 border-dashed border-gray-300 rounded-lg p-4">
                    <div v-if="!imagePreview" class="text-center">
                      <label class="cursor-pointer text-sm text-emerald-600 hover:text-emerald-700 font-medium">
                        Subir imagen
                        <input type="file" accept="image/*" class="hidden" @change="onFileChange" />
                      </label>
                      <p class="text-xs text-gray-400 mt-1">Agrega una foto del punto de acumulación</p>
                    </div>
                    <div v-else class="space-y-2">
                      <img :src="imagePreview" alt="Preview" class="rounded-lg w-full max-w-sm" />
                      <div class="flex gap-2">
                        <BaseButton size="sm" :loading="uploadingImage" @click="handleUploadImage">
                          Subir
                        </BaseButton>
                        <BaseButton size="sm" variant="secondary" @click="clearImage">
                          Cancelar
                        </BaseButton>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>

            <BaseCard>
              <h3 class="text-sm font-medium text-gray-500 mb-3">Ubicación</h3>
              <MapView
                :center="{ lat: report.latitude, lng: report.longitude }"
                :zoom="15"
                :markers="reportMarker"
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
                <div v-if="report.estimated_quantity">
                  <span class="text-gray-500">Cantidad estimada:</span>
                  <p class="font-medium text-gray-900">{{ report.estimated_quantity }} kg</p>
                </div>
                <div v-if="report.cleaner_name">
                  <span class="text-gray-500">Asignado a:</span>
                  <p class="font-medium text-gray-900">{{ report.cleaner_name }}</p>
                </div>
                <div v-if="report.validator_name">
                  <span class="text-gray-500">Validado por:</span>
                  <p class="font-medium text-gray-900">{{ report.validator_name }}</p>
                </div>
                <div v-if="report.validated_at">
                  <span class="text-gray-500">Validado el:</span>
                  <p class="font-medium text-gray-900">{{ formatDate(report.validated_at) }}</p>
                </div>
                <div v-if="report.updated_at !== report.created_at">
                  <span class="text-gray-500">Actualizado:</span>
                  <p class="font-medium text-gray-900">{{ formatDate(report.updated_at) }}</p>
                </div>
              </div>
            </BaseCard>

            <div class="space-y-2">
              <BaseButton
                v-if="canClaim"
                class="w-full"
                :loading="reportStore.loading"
                @click="handleClaim"
              >
                Reclamar tarea
              </BaseButton>
              <BaseButton
                v-if="canComplete"
                variant="primary"
                class="w-full"
                @click="openComplete"
              >
                Marcar como limpiado
              </BaseButton>
              <BaseButton
                v-if="canUnclaim"
                variant="secondary"
                class="w-full"
                @click="openUnclaim"
              >
                Liberar tarea
              </BaseButton>
              <BaseButton
                v-if="canVerify"
                variant="primary"
                class="w-full"
                :loading="reportStore.loading"
                @click="handleVerify"
              >
                Verificar limpieza
              </BaseButton>
              <BaseButton
                v-if="canReject"
                variant="danger"
                class="w-full"
                @click="openReject"
              >
                Rechazar limpieza
              </BaseButton>
              <BaseButton v-if="isOwner() || authStore.isAdmin" variant="secondary" class="w-full" @click="openEdit">
                Editar reporte
              </BaseButton>
              <BaseButton v-if="isOwner() || authStore.isAdmin" variant="danger" class="w-full" :loading="deleting" @click="handleDelete">
                Eliminar
              </BaseButton>
            </div>
          </div>
        </div>
      </template>
    </div>

    <ReportEditModal
      :show="showEditModal"
      :report="report"
      @update:show="showEditModal = $event"
      @save="handleEdit"
    />
    <ReportCompleteModal
      :show="showCompleteModal"
      :report="report"
      @update:show="showCompleteModal = $event"
      @confirm="handleComplete"
    />
    <ReportRejectModal
      :show="showRejectModal"
      :report="report"
      @update:show="showRejectModal = $event"
      @confirm="handleReject"
    />
    <ReportUnclaimModal
      :show="showUnclaimModal"
      :report="report"
      @update:show="showUnclaimModal = $event"
      @confirm="handleUnclaim"
    />
  </AppLayout>
</template>
