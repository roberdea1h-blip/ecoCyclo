<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Reward } from '../../types'
import BaseInput from '../base/BaseInput.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseAlert from '../base/BaseAlert.vue'
import BaseModal from '../base/BaseModal.vue'
import IconParty from '../icons/IconParty.vue'

const props = defineProps<{
  show: boolean
  reward: Reward | null
  userPoints: number
  error: string | null
  redeemSuccess: boolean
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  confirm: [{ delivery_type?: string; delivery_info?: string }]
}>()

const deliveryType = ref('')
const deliveryInfo = ref('')

watch(() => props.show, (val) => {
  if (val) {
    deliveryType.value = ''
    deliveryInfo.value = ''
  }
})

function handleConfirm() {
  const data: { delivery_type?: string; delivery_info?: string } = {}
  if (deliveryType.value) data.delivery_type = deliveryType.value
  if (deliveryInfo.value) data.delivery_info = deliveryInfo.value
  emit('confirm', data)
}
</script>

<template>
  <BaseModal :model-value="show" title="Confirmar canje" @update:model-value="emit('update:show', $event)">
    <div v-if="props.redeemSuccess" class="text-center py-6">
      <IconParty class="w-12 h-12 mx-auto text-emerald-500" />
      <p class="text-lg font-semibold text-gray-900 mt-3">¡Canje exitoso!</p>
      <p class="text-sm text-gray-600 mt-1">
        Has canjeado "{{ reward?.name }}" por {{ reward?.points_cost ?? 0 }} puntos.
      </p>
      <BaseButton class="mt-4" @click="emit('update:show', false)">Cerrar</BaseButton>
    </div>
    <div v-else class="space-y-4">
      <p class="text-gray-700">
        ¿Canjear <strong>{{ reward?.name }}</strong> por
        <strong>{{ reward?.points_cost ?? 0 }}</strong> puntos?
      </p>
      <div class="flex items-center gap-2 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
        <span>Puntos actuales:</span>
        <span class="font-semibold text-gray-900">{{ userPoints }}</span>
        <span class="mx-1">&rarr;</span>
        <span class="font-semibold text-gray-900">{{ userPoints - (reward?.points_cost ?? 0) }}</span>
      </div>
      <BaseInput
        v-model="deliveryType"
        label="Tipo de entrega (opcional)"
        placeholder="Ej: Retiro en tienda, Envío a domicilio"
      />
      <BaseInput
        v-model="deliveryInfo"
        label="Información de entrega (opcional)"
        placeholder="Dirección, instrucciones, etc."
      />
      <BaseAlert v-if="error" variant="error">{{ error }}</BaseAlert>
    </div>
    <template #footer>
      <template v-if="!props.redeemSuccess">
        <BaseButton variant="secondary" @click="emit('update:show', false)">Cancelar</BaseButton>
        <BaseButton :loading="props.loading" @click="handleConfirm">Confirmar canje</BaseButton>
      </template>
    </template>
  </BaseModal>
</template>
