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
  save: [{ title: string; description: string; address: string; estimated_quantity: number | null; status: string }]
}>()

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'cleaned', label: 'Limpiado' },
  { value: 'pending_review', label: 'Pendiente de revisión' },
  { value: 'verified', label: 'Verificado' },
  { value: 'rejected', label: 'Rechazado' },
]

const form = ref({ title: '', description: '', address: '', estimated_quantity: null as number | null, status: '' })

watch(() => props.show, (val) => {
  if (val && props.report) {
    form.value = {
      title: props.report.title,
      description: props.report.description || '',
      address: props.report.address || '',
      estimated_quantity: props.report.estimated_quantity,
      status: props.report.status,
    }
  }
})

function handleSubmit() {
  emit('save', { ...form.value })
}
</script>

<template>
  <BaseModal :model-value="show" title="Editar reporte" @update:model-value="emit('update:show', $event)">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <BaseInput v-model="form.title" label="Título" required />
      <BaseTextarea v-model="form.description" label="Descripción" />
      <BaseInput v-model="form.address" label="Dirección" />
      <BaseInput v-model.number="form.estimated_quantity" label="Cantidad estimada (kg)" type="number" min="0" step="0.1" />
      <BaseSelect v-model="form.status" label="Estado" :options="statusOptions" />
      <div class="flex gap-3">
        <BaseButton type="submit">Guardar</BaseButton>
        <BaseButton type="button" variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
