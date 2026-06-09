import { api } from './http'
import type { Report, User, RewardCreate, Reward } from '../types'

export const adminApi = {
  users() {
    return api.get<User[]>('/admin/users')
  },

  reports() {
    return api.get<Report[]>('/admin/reports')
  },

  createReward(data: RewardCreate) {
    return api.post<Reward>('/admin/rewards', data)
  },

  setup() {
    return api.post<{ message: string }>('/admin/setup')
  },
}
