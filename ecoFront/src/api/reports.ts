import { api } from './http'
import type { Report, ReportCreate, ReportUpdate, PaginatedResponse } from '../types'

export const reportsApi = {
  list(params?: { page?: number; size?: number; status?: string; waste_type_id?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', String(params.page))
    if (params?.size) searchParams.set('size', String(params.size))
    if (params?.status) searchParams.set('status', params.status)
    if (params?.waste_type_id) searchParams.set('waste_type_id', String(params.waste_type_id))
    const qs = searchParams.toString()
    return api.get<PaginatedResponse<Report>>(`/reports${qs ? `?${qs}` : ''}`)
  },

  mine(params?: { page?: number; size?: number }) {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', String(params.page))
    if (params?.size) searchParams.set('size', String(params.size))
    const qs = searchParams.toString()
    return api.get<PaginatedResponse<Report>>(`/reports/mine${qs ? `?${qs}` : ''}`)
  },

  get(id: number) {
    return api.get<Report>(`/reports/${id}`)
  },

  create(data: ReportCreate) {
    const formData = new FormData()
    formData.append('title', data.title)
    formData.append('description', data.description)
    formData.append('latitude', String(data.latitude))
    formData.append('longitude', String(data.longitude))
    formData.append('waste_type_id', String(data.waste_type_id))
    if (data.address) formData.append('address', data.address)
    if (data.image) formData.append('image', data.image)
    return api.postForm<Report>('/reports', formData)
  },

  update(id: number, data: ReportUpdate) {
    return api.patch<Report>(`/reports/${id}`, data)
  },

  delete(id: number) {
    return api.delete<void>(`/reports/${id}`)
  },
}
