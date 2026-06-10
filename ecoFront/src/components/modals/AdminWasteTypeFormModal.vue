<script setup lang="ts">
import { ref, watch } from 'vue'
import type { WasteType, WasteTypeCreate } from '../../types'
import BaseInput from '../base/BaseInput.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'

const props = defineProps<{
  show: boolean
  wasteType: WasteType | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  save: [data: WasteTypeCreate]
}>()

const form = ref<WasteTypeCreate>({ name: '', description: '', icon: '', points_per_report: 10 })

watch(() => props.show, (val) => {
  if (val) {
    if (props.wasteType) {
      form.value = {
        name: props.wasteType.name,
        description: props.wasteType.description || '',
        icon: props.wasteType.icon || '',
        points_per_report: props.wasteType.points_per_report,
      }
    } else {
      form.value = { name: '', description: '', icon: '', points_per_report: 10 }
    }
  }
})

function handleSubmit() {
  if (!form.value.name.trim()) return
  emit('save', { ...form.value })
}
</script>

<template>
  <BaseModal :model-value="show" :title="wasteType ? 'Editar tipo de residuo' : 'Crear tipo de residuo'" @update:model-value="emit('update:show', $event)">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <BaseInput v-model="form.name" label="Nombre" placeholder="Ej: Plástico" required />
      <BaseInput v-model="form.description" label="Descripción" placeholder="Breve descripción del tipo de residuo" />
      <BaseInput v-model="form.icon" label="Icono" placeholder="Identificador del icono" />
      <BaseInput v-model.number="form.points_per_report" label="Puntos por reporte" type="number" min="0" />
      <div class="flex gap-3">
        <BaseButton type="submit">{{ wasteType ? 'Guardar' : 'Crear' }}</BaseButton>
        <BaseButton type="button" variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
