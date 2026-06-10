import { api } from './http'
import type { Reward } from '../types'

export const rewardsApi = {
  list() {
    return api.get<Reward[]>('/rewards')
  },

  get(id: string) {
    return api.get<Reward>(`/rewards/${id}`)
  },

  redeem(id: string) {
    return api.post<{ id: string }>(`/rewards/${id}/redeem`)
  },
}
