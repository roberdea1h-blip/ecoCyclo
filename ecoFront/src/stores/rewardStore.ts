import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Reward } from '../types'
import { rewardsApi } from '../api/rewards'
import { useAuthStore } from './authStore'

export const useRewardStore = defineStore('reward', () => {
  const rewards = ref<Reward[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchRewards() {
    loading.value = true
    error.value = null
    try {
      rewards.value = await rewardsApi.list()
    } catch (e: any) {
      error.value = e.message || 'Error al cargar recompensas'
    } finally {
      loading.value = false
    }
  }

  async function redeemReward(id: string, data?: { delivery_type?: string; delivery_info?: string }) {
    loading.value = true
    error.value = null
    try {
      const result = await rewardsApi.redeem(id, data)
      const reward = rewards.value.find(r => r.id === id)
      if (reward) reward.stock -= 1
      const authStore = useAuthStore()
      await authStore.fetchUser()
      return result
    } catch (e: any) {
      error.value = e.message || 'Error al canjear recompensa'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    rewards,
    loading,
    error,
    fetchRewards,
    redeemReward,
  }
})
