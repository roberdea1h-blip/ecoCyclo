<script setup lang="ts">
import type { Report } from '../../types'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'

defineProps<{
  show: boolean
  report: Report | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  confirm: []
}>()
</script>

<template>
  <BaseModal :model-value="show" title="Liberar tarea" @update:model-value="emit('update:show', $event)">
    <div class="space-y-4">
      <p class="text-gray-700">
        ¿Estás seguro de liberar esta tarea? El reporte volverá a estado <strong>pendiente</strong>
        y estará disponible para otros voluntarios.
      </p>
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      <BaseButton variant="danger" @click="emit('confirm')">Liberar</BaseButton>
    </template>
  </BaseModal>
</template>
