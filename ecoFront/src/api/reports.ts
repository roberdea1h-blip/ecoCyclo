import { api } from './http'
import type { Report, ReportCreate, ReportUpdate } from '../types'

export const reportsApi = {
  list(params?: { skip?: number; limit?: number; status?: string; waste_type_id?: string }) {
    const searchParams = new URLSearchParams()
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.status) searchParams.set('status', params.status)
    if (params?.waste_type_id) searchParams.set('waste_type_id', params.waste_type_id)
    const qs = searchParams.toString()
    return api.get<Report[]>(`/reports${qs ? `?${qs}` : ''}`)
  },

  claimed(params?: { skip?: number; limit?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    const qs = searchParams.toString()
    return api.get<Report[]>(`/reports/claimed${qs ? `?${qs}` : ''}`)
  },

  mine(params?: { skip?: number; limit?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    const qs = searchParams.toString()
    return api.get<Report[]>(`/reports/mine${qs ? `?${qs}` : ''}`)
  },

  get(id: string) {
    return api.get<Report>(`/reports/${id}`)
  },

  create(data: ReportCreate) {
    return api.post<Report>('/reports', data)
  },

  uploadImage(id: string, file: File, isBefore = true) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('is_before', String(isBefore))
    return api.postForm<{ id: string; image_url: string }>(`/reports/${id}/images`, formData)
  },

  claim(id: string) {
    return api.post<Report>(`/reports/${id}/claim`)
  },

  unclaim(id: string) {
    return api.post<Report>(`/reports/${id}/unclaim`)
  },

  complete(id: string, data: { collected_weight?: number; notes?: string }) {
    return api.post<Report>(`/reports/${id}/complete`, data)
  },

  verify(id: string) {
    return api.post<Report>(`/reports/${id}/verify`)
  },

  reject(id: string, data?: { reason?: string }) {
    return api.post<Report>(`/reports/${id}/reject`, data)
  },

  pendingReview(params?: { skip?: number; limit?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params?.limit) searchParams.set('limit', String(params.limit))
    const qs = searchParams.toString()
    return api.get<Report[]>(`/reports/pending-review${qs ? `?${qs}` : ''}`)
  },

  update(id: string, data: ReportUpdate) {
    return api.patch<Report>(`/reports/${id}`, data)
  },

  delete(id: string) {
    return api.delete<void>(`/reports/${id}`)
  },
}
