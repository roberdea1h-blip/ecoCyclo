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
import BaseInput from '../components/base/BaseInput.vue'
import BaseTextarea from '../components/base/BaseTextarea.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import MapView from '../components/maps/MapView.vue'

const route = useRoute()
const router = useRouter()
const reportStore = useReportStore()
const authStore = useAuthStore()

const showEditModal = ref(false)
const editForm = ref({ title: '', description: '', address: '', latitude: 0, longitude: 0, estimated_quantity: null as number | null, status: '' })
const deleting = ref(false)
const showCompleteModal = ref(false)
const collectedWeight = ref<number | undefined>()
const completionNotes = ref('')
const showRejectModal = ref(false)
const rejectReason = ref('')
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const uploadingImage = ref(false)

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'cleaned', label: 'Limpiado' },
  { value: 'pending_review', label: 'Pendiente de revisión' },
  { value: 'verified', label: 'Verificado' },
  { value: 'rejected', label: 'Rechazado' },
]

async function loadReport(id: string) {
  if (!id) {
    router.push('/reports')
    return
  }
  await reportStore.fetchReport(id)
}

onMounted(() => loadReport(route.params.id as string))

watch(() => route.params.id, (newId) => {
  if (newId) loadReport(newId as string)
})

console.log('message');
const report = reportStore.currentReport

const isOwner = () => report.value?.user_id === authStore.user?.id
const isCleaner = () => report.value?.cleaner_id === authStore.user?.id
const canClaim = computed(() => report.value?.status === 'pending' && !isOwner())
const canComplete = computed(() => report.value?.status === 'in_progress' && isCleaner())
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

function openComplete() {
  collectedWeight.value = undefined
  completionNotes.value = ''
  showCompleteModal.value = true
}

async function handleComplete() {
  if (!report.value) return
  try {
    await reportStore.completeReport(report.value.id, {
      collected_weight: collectedWeight.value,
      notes: completionNotes.value || undefined,
    })
    showCompleteModal.value = false
  } catch {
    // handled by store
  }
}

async function handleVerify() {
  if (!report.value) return
  try {
    await reportStore.verifyReport(report.value.id)
  } catch {
    // handled by store
  }
}

function openReject() {
  rejectReason.value = ''
  showRejectModal.value = true
}

async function handleReject() {
  if (!report.value) return
  try {
    await reportStore.rejectReport(report.value.id, rejectReason.value || undefined)
    showRejectModal.value = false
  } catch {
    // handled by store
  }
}

function openEdit() {
  const r = report.value
  if (!r) return
  editForm.value = {
    title: r.title,
    description: r.description || '',
    address: r.address || '',
    latitude: r.latitude,
    longitude: r.longitude,
    estimated_quantity: r.estimated_quantity,
    status: r.status,
  }
  showEditModal.value = true
}

async function handleEdit() {
  if (!report.value) return
  const data: Record<string, any> = {}
  if (editForm.value.title !== report.value.title) data.title = editForm.value.title
  if (editForm.value.description !== (report.value.description || '')) data.description = editForm.value.description || null
  if (editForm.value.address !== (report.value.address || '')) data.address = editForm.value.address || null
  if (editForm.value.estimated_quantity !== report.value.estimated_quantity) data.estimated_quantity = editForm.value.estimated_quantity
  if (editForm.value.status !== report.value.status) data.status = editForm.value.status
  if (editForm.value.latitude !== report.value.latitude) data.latitude = editForm.value.latitude
  if (editForm.value.longitude !== report.value.longitude) data.longitude = editForm.value.longitude
  if (Object.keys(data).length === 0) {
    showEditModal.value = false
    return
  }
  await reportStore.updateReport(report.value.id, data)
  showEditModal.value = false
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

    <BaseModal v-model="showEditModal" title="Editar reporte">
      <form @submit.prevent="handleEdit" class="space-y-4">
        <BaseInput
          v-model="editForm.title"
          label="Título"
          required
        />
        <BaseTextarea
          v-model="editForm.description"
          label="Descripción"
        />
        <BaseInput
          v-model="editForm.address"
          label="Dirección"
        />
        <div class="grid grid-cols-2 gap-3">
            <BaseInput v-model.number="editForm.latitude" label="Latitud" type="number" step="any" />
            <BaseInput v-model.number="editForm.longitude" label="Longitud" type="number" step="any" />
          </div>
          <BaseInput
            v-model.number="editForm.estimated_quantity"
            label="Cantidad estimada (kg)"
            type="number"
            min="0"
            step="0.1"
          />
        <BaseSelect
          v-model="editForm.status"
          label="Estado"
          :options="statusOptions"
        />
        <div class="flex gap-3">
          <BaseButton type="submit" :loading="reportStore.loading">Guardar</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showEditModal = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal v-model="showCompleteModal" title="Completar limpieza">
      <div class="space-y-4">
        <BaseInput
          v-model.number="collectedWeight"
          label="Peso recolectado (kg, opcional)"
          type="number"
          min="0"
          step="0.1"
          placeholder="Ej: 2.5"
        />
        <BaseInput
          v-model="completionNotes"
          label="Notas (opcional)"
          placeholder="Observaciones adicionales..."
        />
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showCompleteModal = false">Cancelar</BaseButton>
        <BaseButton :loading="reportStore.loading" @click="handleComplete">Completar</BaseButton>
      </template>
    </BaseModal>

    <BaseModal v-model="showRejectModal" title="Rechazar limpieza">
      <div class="space-y-4">
        <p class="text-sm text-gray-600">Indica el motivo del rechazo de la limpieza reportada.</p>
        <BaseInput
          v-model="rejectReason"
          label="Motivo (opcional)"
          placeholder="Ej: La limpieza no se completó adecuadamente"
        />
      </div>
      <template #footer>
        <BaseButton variant="secondary" @click="showRejectModal = false">Cancelar</BaseButton>
        <BaseButton variant="danger" :loading="reportStore.loading" @click="handleReject">Rechazar</BaseButton>
      </template>
    </BaseModal>
  </AppLayout>
</template>
