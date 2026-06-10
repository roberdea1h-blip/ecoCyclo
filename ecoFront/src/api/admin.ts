import { api } from './http'
import type { Report, User, RewardCreate, Reward, WasteType, WasteTypeCreate, WasteTypeUpdate } from '../types'

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
}
