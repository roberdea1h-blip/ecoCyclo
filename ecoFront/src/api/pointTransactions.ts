import { api } from './http'
import type { PointTransaction } from '../types'

export const pointTransactionsApi = {
  mine(params?: { skip?: number; limit?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    const qs = searchParams.toString()
    return api.get<PointTransaction[]>(`/point-transactions/me${qs ? `?${qs}` : ''}`)
  },
}
