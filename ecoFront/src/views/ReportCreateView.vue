<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { wasteTypesApi } from '../api/wasteTypes'
import { reportsApi } from '../api/reports'
import { useFormValidation } from '../composables/useFormValidation'
import { reportSchema } from '../utils/validators'
import type { WasteType } from '../types'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseTextarea from '../components/base/BaseTextarea.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import BaseImageUpload from '../components/base/BaseImageUpload.vue'
import LocationPicker from '../components/maps/LocationPicker.vue'

interface LocalCoords {
  lat: number
  lng: number
}

const router = useRouter()
const reportStore = useReportStore()
const { errors, validate } = useFormValidation(reportSchema)

const wasteTypes = ref<WasteType[]>([])
const location = ref<LocalCoords | null>(null)
const imageFile = ref<File | null>(null)
const uploading = ref(false)

const form = reactive({
  title: '',
  description: '',
  waste_type_id: '',
  address: '',
  estimated_quantity: undefined as number | undefined,
})

const wasteOptions = ref<{ value: string; label: string }[]>([])

onMounted(async () => {
  try {
    wasteTypes.value = await wasteTypesApi.list()
    wasteOptions.value = wasteTypes.value.map(wt => ({
      value: wt.id,
      label: wt.name,
    }))
  } catch {
    // silent
  }
})

async function handleSubmit() {
  if (!validate({ ...form })) return
  if (!location.value) {
    alert('Selecciona una ubicación en el mapa')
    return
  }

  try {
    const report = await reportStore.createReport({
      title: form.title,
      description: form.description,
      latitude: location.value.lat,
      longitude: location.value.lng,
      address: form.address || undefined,
      waste_type_id: form.waste_type_id,
      estimated_quantity: form.estimated_quantity,
    })
    if (imageFile.value) {
      uploading.value = true
      await reportsApi.uploadImage(report.id, imageFile.value, true)
    }
    router.push(`/reports/${report.id}`)
  } catch {
    // handled by store
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Nuevo reporte</h1>
        <p class="text-gray-600 mt-1">Reporta un punto de acumulación de basura</p>
      </div>

      <BaseAlert v-if="reportStore.error" variant="error">
        {{ reportStore.error }}
      </BaseAlert>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <BaseInput
          v-model="form.title"
          label="Título"
          placeholder="Ej: Acumulación en esquina"
          required
          :error="errors.title"
        />

        <BaseTextarea
          v-model="form.description"
          label="Descripción"
          placeholder="Describe el punto de acumulación..."
          required
          :error="errors.description"
          :rows="4"
        />

        <BaseSelect
          v-model="form.waste_type_id"
          label="Tipo de residuo"
          :options="wasteOptions"
          placeholder="Selecciona un tipo"
          required
          :error="errors.waste_type_id"
        />

        <BaseInput
          v-model.number="form.estimated_quantity"
          label="Cantidad estimada (kg, opcional)"
          type="number"
          min="0"
          step="0.1"
          placeholder="Ej: 5"
        />

        <BaseImageUpload v-model="imageFile" label="Imagen" />

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Ubicación <span class="text-red-500">*</span>
          </label>
          <LocationPicker v-model="location" />
        </div>

        <BaseInput
          v-model="form.address"
          label="Dirección (opcional)"
          placeholder="Calle, número, colonia..."
        />

        <div class="flex gap-3">
          <BaseButton type="submit" :loading="reportStore.loading || uploading">
            {{ uploading ? 'Subiendo imagen...' : 'Crear reporte' }}
          </BaseButton>
          <router-link to="/reports">
            <BaseButton type="button" variant="secondary">Cancelar</BaseButton>
          </router-link>
        </div>
      </form>
    </div>
  </AppLayout>
</template>
