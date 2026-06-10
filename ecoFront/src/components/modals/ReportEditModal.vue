<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Report } from '../../types'
import BaseInput from '../base/BaseInput.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseSelect from '../base/BaseSelect.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'

const props = defineProps<{
  show: boolean
  report: Report | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  save: [data: Record<string, unknown>]
}>()

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'cleaned', label: 'Limpiado' },
  { value: 'pending_review', label: 'Pendiente de revisión' },
  { value: 'verified', label: 'Verificado' },
  { value: 'rejected', label: 'Rechazado' },
]

const form = ref({
  title: '',
  description: '',
  address: '',
  latitude: 0,
  longitude: 0,
  estimated_quantity: null as number | null,
  status: '',
})

watch(() => props.show, (val) => {
  if (val && props.report) {
    form.value = {
      title: props.report.title,
      description: props.report.description || '',
      address: props.report.address || '',
      latitude: props.report.latitude,
      longitude: props.report.longitude,
      estimated_quantity: props.report.estimated_quantity,
      status: props.report.status,
    }
  }
})

function handleSubmit() {
  const data: Record<string, unknown> = {}
  if (!props.report) return
  if (form.value.title !== props.report.title) data.title = form.value.title
  if (form.value.description !== (props.report.description || '')) data.description = form.value.description || null
  if (form.value.address !== (props.report.address || '')) data.address = form.value.address || null
  if (form.value.estimated_quantity !== props.report.estimated_quantity) data.estimated_quantity = form.value.estimated_quantity
  if (form.value.status !== props.report.status) data.status = form.value.status
  if (form.value.latitude !== props.report.latitude) data.latitude = form.value.latitude
  if (form.value.longitude !== props.report.longitude) data.longitude = form.value.longitude
  if (Object.keys(data).length === 0) {
    emit('update:show', false)
    return
  }
  emit('save', data)
}
</script>

<template>
  <BaseModal :model-value="show" title="Editar reporte" @update:model-value="emit('update:show', $event)">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <BaseInput v-model="form.title" label="Título" required />
      <BaseTextarea v-model="form.description" label="Descripción" />
      <BaseInput v-model="form.address" label="Dirección" />
      <div class="grid grid-cols-2 gap-3">
        <BaseInput v-model.number="form.latitude" label="Latitud" type="number" step="any" />
        <BaseInput v-model.number="form.longitude" label="Longitud" type="number" step="any" />
      </div>
      <BaseInput v-model.number="form.estimated_quantity" label="Cantidad estimada (kg)" type="number" min="0" step="0.1" />
      <BaseSelect v-model="form.status" label="Estado" :options="statusOptions" />
      <div class="flex gap-3">
        <BaseButton type="submit">Guardar</BaseButton>
        <BaseButton type="button" variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
