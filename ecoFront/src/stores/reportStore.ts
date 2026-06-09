import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Report, ReportCreate, ReportUpdate, PaginatedResponse } from '../types'
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
  const filterWasteType = ref<number | undefined>()

  const pendingCount = computed(() => reports.value.filter(r => r.status === 'pending').length)
  const inProgressCount = computed(() => reports.value.filter(r => r.status === 'in_progress').length)
  const resolvedCount = computed(() => reports.value.filter(r => r.status === 'resolved').length)

  async function fetchReports(params?: { page?: number }) {
    loading.value = true
    error.value = null
    try {
      const result = await reportsApi.list({
        page: params?.page || page.value,
        status: filterStatus.value,
        waste_type_id: filterWasteType.value,
      })
      reports.value = result.items
      total.value = result.total
      page.value = result.page
      pages.value = result.pages
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
      const result = await reportsApi.mine({ page: params?.page || 1 })
      reports.value = result.items
      total.value = result.total
      page.value = result.page
      pages.value = result.pages
    } catch (e: any) {
      error.value = e.message || 'Error al cargar tus reportes'
    } finally {
      loading.value = false
    }
  }

  async function fetchReport(id: number) {
    loading.value = true
    error.value = null
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

  async function updateReport(id: number, data: ReportUpdate) {
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

  async function deleteReport(id: number) {
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

  function setFilter(status?: string, wasteTypeId?: number) {
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
    resolvedCount,
    fetchReports,
    fetchMyReports,
    fetchReport,
    createReport,
    updateReport,
    deleteReport,
    setFilter,
  }
})
