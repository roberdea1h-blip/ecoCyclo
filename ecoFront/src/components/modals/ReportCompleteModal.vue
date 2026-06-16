<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Report } from '../../types'
import BaseInput from '../base/BaseInput.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'

const props = defineProps<{
  show: boolean
  report: Report | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  confirm: [{ collected_weight: number; notes?: string }]
}>()

const collectedWeight = ref<number | null>(null)
const completionNotes = ref('')
const weightError = ref('')

watch(() => props.show, (val) => {
  if (val) {
    collectedWeight.value = null
    completionNotes.value = ''
    weightError.value = ''
  }
})

function handleConfirm() {
  if (!collectedWeight.value || collectedWeight.value <= 0) {
    weightError.value = 'El peso es obligatorio y debe ser mayor a 0'
    return
  }
  weightError.value = ''
  emit('confirm', {
    collected_weight: collectedWeight.value,
    notes: completionNotes.value || undefined,
  })
}
</script>

<template>
  <BaseModal :model-value="show" title="Completar limpieza" @update:model-value="emit('update:show', $event)">
    <div class="space-y-4">
      <p v-if="report" class="text-sm text-gray-600">
        Reporte: <strong>{{ report.title }}</strong>
      </p>
      <BaseInput
        v-model.number="collectedWeight"
        label="Peso recolectado (kg)"
        type="number"
        min="0"
        step="0.1"
        placeholder="Ej: 2.5"
        :error="weightError"
      />
      <BaseInput
        v-model="completionNotes"
        label="Notas (opcional)"
        placeholder="Observaciones adicionales..."
      />
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      <BaseButton @click="handleConfirm">Completar</BaseButton>
    </template>
  </BaseModal>
</template>
