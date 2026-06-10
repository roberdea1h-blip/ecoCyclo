import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Reward } from '../types'
import { rewardsApi } from '../api/rewards'
import { useAuthStore } from './authStore'
import { isApiError } from '../types/api-error'
import { useApiError } from '../composables/useApiError'

export const useRewardStore = defineStore('reward', () => {
  const rewards = ref<Reward[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const outOfStockError = ref<string | null>(null)
  const insufficientPointsError = ref<string | null>(null)

  const { handleError, clearError } = useApiError()

  async function fetchRewards() {
    loading.value = true
    clearError()
    try {
      rewards.value = await rewardsApi.list()
    } catch (e: unknown) {
      error.value = handleError(e)
    } finally {
      loading.value = false
    }
  }

  async function redeemReward(id: string, data?: { delivery_type?: string; delivery_info?: string }) {
    loading.value = true
    clearError()
    outOfStockError.value = null
    insufficientPointsError.value = null
    try {
      const result = await rewardsApi.redeem(id, data)
      const reward = rewards.value.find(r => r.id === id)
      if (reward) reward.stock -= 1
      const authStore = useAuthStore()
      await authStore.fetchUser()
      return result
    } catch (e: unknown) {
      if (isApiError(e)) {
        if (e.error_code === 'reward_out_of_stock') {
          outOfStockError.value = 'La recompensa está agotada.'
        } else if (e.error_code === 'insufficient_points' || e.error_code === 'insufficient_points_for_redemption') {
          insufficientPointsError.value = 'No tienes suficientes puntos para canjear esta recompensa.'
        } else {
          error.value = handleError(e)
        }
      } else {
        error.value = 'Error inesperado. Intenta de nuevo.'
      }
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    rewards,
    loading,
    error,
    outOfStockError,
    insufficientPointsError,
    fetchRewards,
    redeemReward,
  }
})
