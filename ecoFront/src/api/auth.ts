import { api } from './http'
import type { AuthTokens, User } from '../types'

export const authApi = {
  register(data: { email: string; password: string; full_name: string }) {
    return api.post<AuthTokens>('/auth/register', data)
  },

  login(data: { email: string; password: string }) {
    return api.post<AuthTokens>('/auth/login', data)
  },

  refresh() {
    return api.post<AuthTokens>('/auth/refresh')
  },

  logout() {
    return api.post<void>('/auth/logout')
  },

  me() {
    return api.get<User>('/auth/me')
  },
}
