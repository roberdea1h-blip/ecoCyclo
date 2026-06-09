import { api } from './http'
import type { Reward } from '../types'

export const rewardsApi = {
  list() {
    return api.get<Reward[]>('/rewards')
  },

  get(id: number) {
    return api.get<Reward>(`/rewards/${id}`)
  },

  redeem(id: number) {
    return api.post<{ message: string }>(`/rewards/${id}/redeem`)
  },
}
