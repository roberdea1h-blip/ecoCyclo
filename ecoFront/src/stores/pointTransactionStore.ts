import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PointTransaction } from '../types'
import { pointTransactionsApi } from '../api/pointTransactions'

export const usePointTransactionStore = defineStore('pointTransaction', () => {
  const transactions = ref<PointTransaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTransactions(limit = 50) {
    loading.value = true
    error.value = null
    try {
      transactions.value = await pointTransactionsApi.mine({ limit })
    } catch (e: any) {
      error.value = e.message || 'Error al cargar historial'
    } finally {
      loading.value = false
    }
  }

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
  }
})
