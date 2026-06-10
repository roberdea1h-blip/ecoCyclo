<script setup lang="ts">
import { ref } from 'vue'
import { adminApi } from '../../api/admin'
import BaseAlert from '../base/BaseAlert.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseCard from '../base/BaseCard.vue'

const setupLoading = ref(false)
const setupResult = ref<string | null>(null)

async function handleSetup() {
  if (!confirm('¿Ejecutar setup inicial? Esto puede crear datos iniciales en el sistema.')) return
  setupLoading.value = true
  setupResult.value = null
  try {
    const result = await adminApi.setup()
    setupResult.value = result.message || 'Setup completado'
  } catch (e: any) {
    setupResult.value = e.message || 'Error en setup'
  } finally {
    setupLoading.value = false
  }
}
</script>

<template>
  <BaseCard>
    <h2 class="text-lg font-semibold text-gray-900 mb-2">Setup inicial</h2>
    <p class="text-sm text-gray-600 mb-4">Ejecuta la configuración inicial del sistema para crear datos por defecto.</p>
    <BaseButton :loading="setupLoading" @click="handleSetup">Ejecutar setup</BaseButton>
    <BaseAlert v-if="setupResult" :variant="setupResult.includes('Error') ? 'error' : 'success'" class="mt-4">
      {{ setupResult }}
    </BaseAlert>
  </BaseCard>
</template>
