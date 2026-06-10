<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps<{
  modelValue: File | null
  label?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: File | null]
}>()

const imagePreview = ref<string | null>(null)

watch(() => props.modelValue, (file) => {
  if (!file) {
    revokePreview()
    imagePreview.value = null
  }
})

onUnmounted(() => {
  revokePreview()
})

function revokePreview() {
  if (imagePreview.value) {
    URL.revokeObjectURL(imagePreview.value)
  }
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    revokePreview()
    imagePreview.value = URL.createObjectURL(file)
    emit('update:modelValue', file)
  }
}

function clearImage() {
  revokePreview()
  imagePreview.value = null
  emit('update:modelValue', null)
}
</script>

<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }} <span class="text-gray-400">(opcional)</span>
    </label>
    <div v-if="!imagePreview" class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
      <label class="cursor-pointer text-sm text-emerald-600 hover:text-emerald-700 font-medium">
        Seleccionar imagen
        <input type="file" accept="image/*" class="hidden" @change="onFileChange" />
      </label>
      <p class="text-xs text-gray-400 mt-1">JPG, PNG o WebP</p>
    </div>
    <div v-else class="space-y-2">
      <img :src="imagePreview" alt="Preview" class="rounded-lg w-full max-w-sm" />
      <BaseButton variant="secondary" size="sm" @click="clearImage">Quitar imagen</BaseButton>
    </div>
  </div>
</template>
