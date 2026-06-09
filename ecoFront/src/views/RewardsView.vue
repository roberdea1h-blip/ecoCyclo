<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRewardStore } from '../stores/rewardStore'
import { useAuthStore } from '../stores/authStore'
import { formatPoints } from '../utils/format'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import IconGift from '../components/icons/IconGift.vue'
import IconParty from '../components/icons/IconParty.vue'
import IconStar from '../components/icons/IconStar.vue'
import type { Reward } from '../types'

const rewardStore = useRewardStore()
const authStore = useAuthStore()

const selectedReward = ref<Reward | null>(null)
const showConfirmModal = ref(false)
const redeemSuccess = ref(false)

onMounted(async () => {
  await rewardStore.fetchRewards()
})

function openConfirm(reward: Reward) {
  selectedReward.value = reward
  redeemSuccess.value = false
  showConfirmModal.value = true
}

async function confirmRedeem() {
  if (!selectedReward.value) return
  try {
    await rewardStore.redeemReward(selectedReward.value.id)
    redeemSuccess.value = true
    // Actualizar puntos del usuario
    if (authStore.user) {
      authStore.user.points -= selectedReward.value.points_cost
    }
  } catch {
    // handled by store
  }
}
</script>

<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Recompensas</h1>
          <p class="text-gray-600 mt-1">Canjea tus puntos por recompensas</p>
        </div>
        <div class="flex items-center gap-2 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2">
          <IconStar class="w-5 h-5 text-yellow-600" />
          <span class="text-yellow-600 font-semibold">{{ formatPoints(authStore.userPoints) }}</span>
          <span class="text-yellow-700 text-sm">puntos</span>
        </div>
      </div>

      <BaseAlert v-if="rewardStore.error" variant="error" dismissible @dismiss="rewardStore.error = null">
        {{ rewardStore.error }}
      </BaseAlert>

      <BaseSpinner v-if="rewardStore.loading && rewardStore.rewards.length === 0" size="md" />

      <div v-else-if="rewardStore.rewards.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-lg">No hay recompensas disponibles</p>
        <p class="text-sm mt-1">Vuelve pronto</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <BaseCard v-for="reward in rewardStore.rewards" :key="reward.id" class="flex flex-col">
          <div class="flex-1 space-y-3">
            <div class="w-full h-40 bg-gray-100 rounded-lg flex items-center justify-center">
              <IconGift class="w-12 h-12 text-gray-400" />
            </div>
            <h3 class="font-semibold text-gray-900">{{ reward.name }}</h3>
            <p class="text-sm text-gray-600">{{ reward.description }}</p>
            <div class="flex items-center justify-between text-sm">
              <span class="font-bold text-emerald-600">{{ formatPoints(reward.points_cost) }} pts</span>
              <BaseBadge :variant="reward.stock > 0 ? 'success' : 'danger'" size="sm">
                {{ reward.stock > 0 ? `${reward.stock} disponibles` : 'Agotado' }}
              </BaseBadge>
            </div>
          </div>
          <BaseButton
            class="w-full mt-4"
            :disabled="reward.stock <= 0 || authStore.userPoints < reward.points_cost"
            @click="openConfirm(reward)"
          >
            {{ authStore.userPoints >= reward.points_cost ? 'Canjear' : 'Puntos insuficientes' }}
          </BaseButton>
        </BaseCard>
      </div>
    </div>

    <BaseModal v-model="showConfirmModal" title="Confirmar canje">
      <div v-if="redeemSuccess" class="text-center py-6">
        <IconParty class="w-12 h-12 mx-auto text-emerald-500" />
        <p class="text-lg font-semibold text-gray-900 mt-3">¡Canje exitoso!</p>
        <p class="text-sm text-gray-600 mt-1">
          Has canjeado "{{ selectedReward?.name }}" por {{ formatPoints(selectedReward?.points_cost || 0) }} puntos.
        </p>
        <BaseButton class="mt-4" @click="showConfirmModal = false">Cerrar</BaseButton>
      </div>
      <div v-else class="space-y-4">
        <p class="text-gray-700">
          ¿Canjear <strong>{{ selectedReward?.name }}</strong> por
          <strong>{{ formatPoints(selectedReward?.points_cost || 0) }}</strong> puntos?
        </p>
        <div class="flex items-center gap-2 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          <span>Puntos actuales:</span>
          <span class="font-semibold text-gray-900">{{ formatPoints(authStore.userPoints) }}</span>
          <span class="mx-1">&rarr;</span>
          <span class="font-semibold text-gray-900">{{ formatPoints(authStore.userPoints - (selectedReward?.points_cost || 0)) }}</span>
        </div>
        <BaseAlert v-if="rewardStore.error" variant="error">
          {{ rewardStore.error }}
        </BaseAlert>
      </div>
      <template #footer>
        <template v-if="!redeemSuccess">
          <BaseButton variant="secondary" @click="showConfirmModal = false">Cancelar</BaseButton>
          <BaseButton :loading="rewardStore.loading" @click="confirmRedeem">Confirmar canje</BaseButton>
        </template>
      </template>
    </BaseModal>
  </AppLayout>
</template>
