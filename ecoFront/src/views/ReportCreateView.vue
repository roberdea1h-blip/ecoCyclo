<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReportStore } from '../stores/reportStore'
import { wasteTypesApi } from '../api/wasteTypes'
import { useFormValidation } from '../composables/useFormValidation'
import { reportSchema } from '../utils/validators'
import type { WasteType } from '../types'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseTextarea from '../components/base/BaseTextarea.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import LocationPicker from '../components/maps/LocationPicker.vue'

// Re-export MapCoordinates type for the LocationPicker
// Esto es necesario porque el componente espera MapCoordinates
// pero el type index.ts no lo tiene. Lo definimos localmente.
interface LocalCoords {
  lat: number
  lng: number
}

const router = useRouter()
const reportStore = useReportStore()
const { errors, validate } = useFormValidation(reportSchema)

const wasteTypes = ref<WasteType[]>([])
const imageFile = ref<File | null>(null)
const imagePreview = ref<string | null>(null)
const location = ref<LocalCoords | null>(null)

const form = reactive({
  title: '',
  description: '',
  waste_type_id: '' as string | number,
  address: '',
})

const wasteOptions = ref<{ value: string | number; label: string }[]>([])

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

async function handleSubmit() {
  if (!validate({ ...form })) return
  if (!location.value) {
    alert('Selecciona una ubicación en el mapa')
    return
  }

  try {
    await reportStore.createReport({
      title: form.title,
      description: form.description,
      latitude: location.value.lat,
      longitude: location.value.lng,
      address: form.address || undefined,
      waste_type_id: Number(form.waste_type_id),
      image: imageFile.value || undefined,
    })
    router.push('/reports')
  } catch {
    // handled by store
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

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Imagen (opcional)
          </label>
          <div class="flex items-center gap-4">
            <label class="cursor-pointer px-4 py-2 bg-gray-100 rounded-lg text-sm text-gray-700 hover:bg-gray-200 transition-colors">
              Seleccionar imagen
              <input type="file" accept="image/*" class="hidden" @change="onFileChange" />
            </label>
            <button
              v-if="imagePreview"
              type="button"
              class="text-sm text-red-600 hover:text-red-700"
              @click="clearImage"
            >
              Eliminar
            </button>
          </div>
          <img v-if="imagePreview" :src="imagePreview" alt="Preview" class="mt-2 w-full max-w-sm rounded-lg" />
        </div>

        <div class="flex gap-3">
          <BaseButton type="submit" :loading="reportStore.loading">
            Crear reporte
          </BaseButton>
          <router-link to="/reports">
            <BaseButton type="button" variant="secondary">Cancelar</BaseButton>
          </router-link>
        </div>
      </form>
    </div>
  </AppLayout>
</template>
