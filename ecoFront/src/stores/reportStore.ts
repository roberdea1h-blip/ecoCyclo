import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Report, ReportCreate, ReportUpdate } from '../types'
import { reportsApi } from '../api/reports'

export const useReportStore = defineStore('report', () => {
  const reports = ref<Report[]>([])
  const currentReport = ref<Report | null>(null)
  const total = ref(0)
  const page = ref(1)
  const pages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filterStatus = ref<string | undefined>()
  const filterWasteType = ref<string | undefined>()

  const pendingCount = computed(() => reports.value.filter(r => r.status === 'pending').length)
  const inProgressCount = computed(() => reports.value.filter(r => r.status === 'in_progress').length)
  const cleanedCount = computed(() => reports.value.filter(r => r.status === 'cleaned').length)
  const pendingReviewCount = computed(() => reports.value.filter(r => r.status === 'pending_review').length)
  const verifiedCount = computed(() => reports.value.filter(r => r.status === 'verified').length)

  async function fetchReports(params?: { page?: number }) {
    loading.value = true
    error.value = null
    try {
      const p = params?.page || page.value
      const result = await reportsApi.list({
        skip: (p - 1) * 20,
        limit: 20,
        status: filterStatus.value,
        waste_type_id: filterWasteType.value,
      })
      reports.value = result || []
      total.value = result.length
      page.value = p
      pages.value = 0
    } catch (e: any) {
      error.value = e.message || 'Error al cargar reportes'
    } finally {
      loading.value = false
    }
  }

  async function fetchMyReports(params?: { page?: number }) {
    loading.value = true
    error.value = null
    try {
      const result = await reportsApi.mine({
        skip: 0,
        limit: 100,
      })
      reports.value = result || []
      total.value = result.length
      page.value = 1
      pages.value = 0
    } catch (e: any) {
      error.value = e.message || 'Error al cargar tus reportes'
    } finally {
      loading.value = false
    }
  }

  async function fetchReport(id: string) {
    loading.value = true
    error.value = null
    currentReport.value = null
    try {
      currentReport.value = await reportsApi.get(id)
    } catch (e: any) {
      error.value = e.message || 'Error al cargar el reporte'
    } finally {
      loading.value = false
    }
  }

  async function createReport(data: ReportCreate) {
    loading.value = true
    error.value = null
    try {
      const report = await reportsApi.create(data)
      reports.value.unshift(report)
      return report
    } catch (e: any) {
      error.value = e.message || 'Error al crear reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateReport(id: string, data: ReportUpdate) {
    loading.value = true
    error.value = null
    try {
      const updated = await reportsApi.update(id, data)
      const idx = reports.value.findIndex(r => r.id === id)
      if (idx !== -1) reports.value[idx] = updated
      if (currentReport.value?.id === id) currentReport.value = updated
      return updated
    } catch (e: any) {
      error.value = e.message || 'Error al actualizar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteReport(id: string) {
    loading.value = true
    error.value = null
    try {
      await reportsApi.delete(id)
      reports.value = reports.value.filter(r => r.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Error al eliminar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function claimReport(id: string) {
    loading.value = true
    error.value = null
    try {
      const updated = await reportsApi.claim(id)
      const idx = reports.value.findIndex(r => r.id === id)
      if (idx !== -1) reports.value[idx] = updated
      if (currentReport.value?.id === id) currentReport.value = updated
      return updated
    } catch (e: any) {
      error.value = e.message || 'Error al reclamar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function completeReport(id: string, data: { collected_weight?: number; notes?: string }) {
    loading.value = true
    error.value = null
    try {
      const updated = await reportsApi.complete(id, data)
      const idx = reports.value.findIndex(r => r.id === id)
      if (idx !== -1) reports.value[idx] = updated
      if (currentReport.value?.id === id) currentReport.value = updated
      return updated
    } catch (e: any) {
      error.value = e.message || 'Error al completar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function verifyReport(id: string) {
    loading.value = true
    error.value = null
    try {
      const updated = await reportsApi.verify(id)
      const idx = reports.value.findIndex(r => r.id === id)
      if (idx !== -1) reports.value[idx] = updated
      if (currentReport.value?.id === id) currentReport.value = updated
      return updated
    } catch (e: any) {
      error.value = e.message || 'Error al verificar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function rejectReport(id: string, reason?: string) {
    loading.value = true
    error.value = null
    try {
      const updated = await reportsApi.reject(id, { reason })
      const idx = reports.value.findIndex(r => r.id === id)
      if (idx !== -1) reports.value[idx] = updated
      if (currentReport.value?.id === id) currentReport.value = updated
      return updated
    } catch (e: any) {
      error.value = e.message || 'Error al rechazar reporte'
      throw e
    } finally {
      loading.value = false
    }
  }

  function setFilter(status?: string, wasteTypeId?: string) {
    filterStatus.value = status
    filterWasteType.value = wasteTypeId
    page.value = 1
  }

  return {
    reports,
    currentReport,
    total,
    page,
    pages,
    loading,
    error,
    filterStatus,
    filterWasteType,
    pendingCount,
    inProgressCount,
    cleanedCount,
    pendingReviewCount,
    verifiedCount,
    fetchReports,
    fetchMyReports,
    fetchReport,
    createReport,
    updateReport,
    deleteReport,
    claimReport,
    completeReport,
    setFilter,
  }
})
