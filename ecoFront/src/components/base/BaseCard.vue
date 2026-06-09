<script setup lang="ts">
withDefaults(defineProps<{
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}>(), {
  padding: 'md',
  hover: false,
})
</script>

<template>
  <div
    class="bg-white rounded-xl border border-gray-200 shadow-sm"
    :class="[
      padding === 'none' && '',
      padding === 'sm' && 'p-3',
      padding === 'md' && 'p-4 sm:p-6',
      padding === 'lg' && 'p-6 sm:p-8',
      hover && 'hover:shadow-md transition-shadow cursor-pointer',
    ]"
  >
    <slot />
  </div>
</template>
