import { api } from './http'
import type { User } from '../types'

export const authApi = {
  register(data: { email: string; password: string; full_name: string }) {
    return api.post<User>('/auth/register', data)
  },

  login(data: { email: string; password: string }) {
    return api.post<{ authenticated: boolean; user: User }>('/auth/login', data)
  },

  refresh() {
    return api.post<{ authenticated: boolean }>('/auth/refresh')
  },

  logout() {
    return api.post<void>('/auth/logout')
  },

  me() {
    return api.get<User>('/auth/me')
  },
}
