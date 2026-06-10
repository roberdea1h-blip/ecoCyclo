<script setup lang="ts">
import { ref, watch } from 'vue'
import { useFormValidation } from '../../composables/useFormValidation'
import { rewardSchema } from '../../utils/validators'
import BaseInput from '../base/BaseInput.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseModal from '../base/BaseModal.vue'
import BaseImageUpload from '../base/BaseImageUpload.vue'

const props = defineProps<{
  show: boolean
  rewardCreated: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  save: [{ data: { name: string; description: string; points_cost: number; stock: number }; imageFile: File | null }]
}>()

const { errors, validate } = useFormValidation(rewardSchema)

const form = ref({ name: '', description: '', points_cost: 0, stock: 0 })
const rewardImageFile = ref<File | null>(null)

watch(() => props.show, (val) => {
  if (val) {
    form.value = { name: '', description: '', points_cost: 0, stock: 0 }
    rewardImageFile.value = null
  }
})

function handleSubmit() {
  const data = {
    name: form.value.name,
    description: form.value.description,
    points_cost: Number(form.value.points_cost) || 0,
    stock: Number(form.value.stock) || 0,
  }
  if (!validate(data)) return
  emit('save', { data, imageFile: rewardImageFile.value })
}
</script>

<template>
  <BaseModal :model-value="show" title="Crear recompensa" @update:model-value="emit('update:show', $event)">
    <div v-if="props.rewardCreated" class="text-center py-6">
      <span class="text-4xl">✅</span>
      <p class="text-lg font-semibold text-gray-900 mt-3">Recompensa creada</p>
      <BaseButton class="mt-4" @click="emit('update:show', false)">Cerrar</BaseButton>
    </div>
    <form v-else @submit.prevent="handleSubmit" class="space-y-4">
      <BaseInput v-model="form.name" label="Nombre" required :error="errors.name" />
      <BaseTextarea v-model="form.description" label="Descripción" required :error="errors.description" />
      <BaseInput v-model="form.points_cost" label="Costo en puntos" type="number" required :error="errors.points_cost" />
      <BaseInput v-model="form.stock" label="Stock" type="number" required :error="errors.stock" />
      <BaseImageUpload v-model="rewardImageFile" label="Imagen" />
      <div class="flex gap-3">
        <BaseButton type="submit">Crear</BaseButton>
        <BaseButton type="button" variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>
