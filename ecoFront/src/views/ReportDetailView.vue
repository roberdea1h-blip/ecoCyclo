<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { useAuthStore } from '../stores/authStore'
import { getStatusLabel, formatDate } from '../utils/format'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseInput from '../components/base/BaseInput.vue'
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
const showCompleteModal = ref(false)
const collectedWeight = ref<number | undefined>()
const completionNotes = ref('')
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const uploadingImage = ref(false)

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'cleaned', label: 'Limpiado' },
]

onMounted(async () => {
  const id = route.params.id as string
  if (!id) {
    router.push('/reports')
    return
  }
  await reportStore.fetchReport(id)
})

const report = reportStore.currentReport
const isOwner = () => report.value?.user_id === authStore.user?.id
const isCleaner = () => report.value?.cleaner_id === authStore.user?.id
const canClaim = computed(() => report.value?.status === 'pending' && !isOwner())
const canComplete = computed(() => report.value?.status === 'in_progress' && isCleaner())

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

function openEdit() {
  editStatus.value = report.value?.status || 'pending'
  showEditModal.value = true
}

async function handleEdit() {
  if (!report.value) return
  await reportStore.updateReport(report.value.id, { status: editStatus.value })
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
              :variant="report.status === 'cleaned' ? 'success' : report.status === 'pending' ? 'warning' : 'info'"
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
                    <img :src="report.image_url" alt="Report" class="rounded-lg w-full max-w-md" />
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
              <BaseButton v-if="isOwner()" variant="secondary" class="w-full" @click="openEdit">
                Cambiar estado
              </BaseButton>
              <BaseButton v-if="isOwner()" variant="danger" class="w-full" :loading="deleting" @click="handleDelete">
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
  </AppLayout>
</template>
