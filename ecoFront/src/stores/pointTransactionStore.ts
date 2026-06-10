import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PointTransaction } from '../types'
import { pointTransactionsApi } from '../api/pointTransactions'
import { useApiError } from '../composables/useApiError'

export const usePointTransactionStore = defineStore('pointTransaction', () => {
  const transactions = ref<PointTransaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const { handleError, clearError } = useApiError()

  async function fetchTransactions(limit = 50) {
    loading.value = true
    clearError()
    try {
      transactions.value = await pointTransactionsApi.mine({ limit })
    } catch (e: unknown) {
      error.value = handleError(e)
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
