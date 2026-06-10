<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Reward } from '../../types'
import BaseInput from '../base/BaseInput.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'

const props = defineProps<{
  show: boolean
  reward: Reward | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  save: [{ name: string; description: string; points_cost: number; stock: number }]
}>()

const form = ref({ name: '', description: '', points_cost: 0, stock: 0 })

watch(() => props.show, (val) => {
  if (val && props.reward) {
    form.value = {
      name: props.reward.name,
      description: props.reward.description,
      points_cost: props.reward.points_cost,
      stock: props.reward.stock ?? 0,
    }
  }
})

function handleSubmit() {
  emit('save', { ...form.value })
}
</script>

<template>
  <BaseModal :model-value="show" title="Editar recompensa" @update:model-value="emit('update:show', $event)">
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <BaseInput v-model="form.name" label="Nombre" required />
      <BaseTextarea v-model="form.description" label="Descripción" required />
      <BaseInput v-model.number="form.points_cost" label="Costo en puntos" type="number" required />
      <BaseInput v-model.number="form.stock" label="Stock" type="number" required />
      <div class="flex gap-3">
        <BaseButton type="submit">Guardar</BaseButton>
        <BaseButton type="button" variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
