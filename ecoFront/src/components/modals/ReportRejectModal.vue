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
  confirm: [{ reason?: string }]
}>()

const rejectReason = ref('')

watch(() => props.show, (val) => {
  if (val) rejectReason.value = ''
})

function handleConfirm() {
  emit('confirm', { reason: rejectReason.value || undefined })
}
</script>

<template>
  <BaseModal :model-value="show" title="Rechazar limpieza" @update:model-value="emit('update:show', $event)">
    <div class="space-y-4">
      <p v-if="report" class="text-sm text-gray-600">
        Reporte: <strong>{{ report.title }}</strong>
      </p>
      <p class="text-sm text-gray-600">Indica el motivo del rechazo de la limpieza reportada.</p>
      <BaseInput
        v-model="rejectReason"
        label="Motivo (opcional)"
        placeholder="Ej: La limpieza no se completó adecuadamente"
      />
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      <BaseButton variant="danger" @click="handleConfirm">Rechazar</BaseButton>
    </template>
  </BaseModal>
</template>
