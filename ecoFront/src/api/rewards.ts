import { api } from './http'
import type { Redemption, Reward, RedeemRequest } from '../types'

export const rewardsApi = {
  list() {
    return api.get<Reward[]>('/rewards')
  },

  get(id: string) {
    return api.get<Reward>(`/rewards/${id}`)
  },

  redeem(id: string, data?: RedeemRequest) {
    return api.post<Redemption>(`/rewards/${id}/redeem`, data)
  },
}
