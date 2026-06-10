<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import { getRedemptionStatusLabel, formatDate, formatPoints } from '../../utils/format'
import type { Redemption } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSelect from '../base/BaseSelect.vue'
import BaseSpinner from '../base/BaseSpinner.vue'

const redemptions = ref<Redemption[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const statusUpdating = ref<string | null>(null)

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'processing', label: 'Procesando' },
  { value: 'activated', label: 'Activado' },
  { value: 'shipped', label: 'Enviado' },
  { value: 'delivered', label: 'Entregado' },
  { value: 'cancelled', label: 'Cancelado' },
]

onMounted(async () => {
  loading.value = true
  try {
    redemptions.value = await adminApi.redemptions()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar canjes'
  } finally {
    loading.value = false
  }
})

async function fetchRedemptions() {
  loading.value = true
  error.value = null
  try {
    redemptions.value = await adminApi.redemptions()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar canjes'
  } finally {
    loading.value = false
  }
}

async function handleUpdateStatus(id: string, status: string) {
  statusUpdating.value = id
  try {
    const updated = await adminApi.updateRedemptionStatus(id, { status })
    const idx = redemptions.value.findIndex(r => r.id === id)
    if (idx !== -1) redemptions.value[idx] = updated
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar estado del canje'
  } finally {
    statusUpdating.value = null
  }
}
</script>

<template>
  <div>
    <div class="flex justify-end mb-4">
      <BaseButton variant="secondary" size="sm" @click="fetchRedemptions">Actualizar</BaseButton>
    </div>
    <BaseSpinner v-if="loading" size="md" />
    <p v-else-if="error" class="text-red-600 text-sm">{{ error }}</p>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 text-left text-gray-500">
            <th class="pb-3 font-medium">ID</th>
            <th class="pb-3 font-medium">Usuario</th>
            <th class="pb-3 font-medium">Recompensa</th>
            <th class="pb-3 font-medium">Puntos</th>
            <th class="pb-3 font-medium">Estado</th>
            <th class="pb-3 font-medium">Fecha</th>
            <th class="pb-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in redemptions" :key="r.id" class="border-b border-gray-100">
            <td class="py-3 text-gray-500 text-xs">{{ r.id }}</td>
            <td class="py-3 font-medium text-gray-900">{{ r.user_id }}</td>
            <td class="py-3 text-gray-600">{{ r.reward_id }}</td>
            <td class="py-3">{{ formatPoints(r.points_spent) }}</td>
            <td class="py-3">
              <BaseBadge
                size="sm"
                :variant="r.status === 'delivered' ? 'success' : r.status === 'cancelled' ? 'danger' : 'info'"
              >
                {{ getRedemptionStatusLabel(r.status) }}
              </BaseBadge>
            </td>
            <td class="py-3 text-gray-500">{{ formatDate(r.redeemed_at) }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <BaseSelect
                  :model-value="r.status"
                  :options="statusOptions"
                  :disabled="statusUpdating === r.id"
                  @update:model-value="(val: string) => handleUpdateStatus(r.id, val)"
                />
              </div>
            </td>
          </tr>
          <tr v-if="redemptions.length === 0">
            <td colspan="7" class="py-8 text-center text-gray-400">
              No hay canjes registrados.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
