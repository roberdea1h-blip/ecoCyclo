<script setup lang="ts">
interface SelectOption {
  value: string | number
  label: string
}

const props = defineProps<{
  modelValue: string | number
  label?: string
  options: SelectOption[]
  placeholder?: string
  error?: string
  disabled?: boolean
  required?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
}>()

function onChange(e: Event) {
  const target = e.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      class="block w-full rounded-lg border px-3 py-2 text-sm shadow-sm transition-colors focus:outline-none focus:ring-2 disabled:bg-gray-50 disabled:text-gray-500"
      :class="error ? 'border-red-300 focus:border-red-400 focus:ring-red-200' : 'border-gray-300 focus:border-emerald-400 focus:ring-emerald-200'"
      @change="onChange"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="opt in options"
        :key="opt.value"
        :value="opt.value"
      >
        {{ opt.label }}
      </option>
    </select>
    <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
  </div>
</template>
