<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'info' | 'success' | 'warning' | 'error'
  dismissible?: boolean
}>(), {
  variant: 'info',
  dismissible: false,
})

const emit = defineEmits<{
  dismiss: []
}>()
</script>

<template>
  <div
    class="flex items-start gap-3 p-4 rounded-lg border"
    :class="[
      variant === 'info' && 'bg-blue-50 border-blue-200 text-blue-800',
      variant === 'success' && 'bg-green-50 border-green-200 text-green-800',
      variant === 'warning' && 'bg-yellow-50 border-yellow-200 text-yellow-800',
      variant === 'error' && 'bg-red-50 border-red-200 text-red-800',
    ]"
  >
    <div class="flex-1 text-sm">
      <slot />
    </div>
    <button
      v-if="dismissible"
      class="shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity"
      @click="emit('dismiss')"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
