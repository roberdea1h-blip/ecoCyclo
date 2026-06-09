<script setup lang="ts">
defineProps<{ type: string }>()
</script>

<template>
  <IconGift v-if="type === 'reward'" />
  <IconReport v-else-if="type === 'report'" />
  <IconStar v-else-if="type === 'points'" />
  <IconBell v-else />
</template>
