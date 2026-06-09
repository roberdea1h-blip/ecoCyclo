<script setup lang="ts">
const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  error?: string
  disabled?: boolean
  required?: boolean
  rows?: number
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

function onInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      :rows="rows || 4"
      class="block w-full rounded-lg border px-3 py-2 text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 disabled:bg-gray-50 disabled:text-gray-500 resize-vertical"
      :class="error ? 'border-red-300 focus:border-red-400 focus:ring-red-200' : 'border-gray-300 focus:border-emerald-400 focus:ring-emerald-200'"
      @input="onInput"
    />
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </div>
</template>
