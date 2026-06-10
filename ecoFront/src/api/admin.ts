import { api } from './http'
import type { Redemption, Report, User, RewardCreate, Reward, RewardUpdate, WasteType, WasteTypeCreate, WasteTypeUpdate } from '../types'

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

  updateReward(id: string, data: RewardUpdate) {
    return api.patch<Reward>(`/admin/rewards/${id}`, data)
  },

  deleteReward(id: string) {
    return api.delete<void>(`/admin/rewards/${id}`)
  },

  uploadRewardImage(rewardId: string, formData: FormData) {
    return api.postForm<Reward>(`/admin/rewards/${rewardId}/image`, formData)
  },

  setup() {
    return api.post<{ message: string }>('/admin/setup')
  },

  wasteTypes() {
    return api.get<WasteType[]>('/admin/waste-types')
  },

  createWasteType(data: WasteTypeCreate) {
    return api.post<WasteType>('/admin/waste-types', data)
  },

  updateWasteType(id: string, data: WasteTypeUpdate) {
    return api.patch<WasteType>(`/admin/waste-types/${id}`, data)
  },

  deleteWasteType(id: string) {
    return api.delete<void>(`/admin/waste-types/${id}`)
  },

  deleteUser(id: string) {
    return api.delete<void>(`/admin/users/${id}`)
  },

  redemptions() {
    return api.get<Redemption[]>('/admin/redemptions')
  },

  updateRedemptionStatus(id: string, data: { status: string }) {
    return api.patch<Redemption>(`/admin/redemptions/${id}/status`, data)
  },
}
