<script setup lang="ts">
withDefaults(defineProps<{
  size?: 'sm' | 'md' | 'lg'
  text?: string
}>(), {
  size: 'md',
  text: 'Cargando...',
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-3 py-12">
    <svg
      class="animate-spin text-emerald-600"
      :class="{
        'w-5 h-5': size === 'sm',
        'w-8 h-8': size === 'md',
        'w-12 h-12': size === 'lg',
      }"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
    <p v-if="text" class="text-sm text-gray-500">{{ text }}</p>
  </div>
</template>
