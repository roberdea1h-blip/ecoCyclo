export function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatPoints(points: number): string {
  return points.toLocaleString('es-ES')
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    cleaned: 'bg-green-100 text-green-800',
    pending_review: 'bg-purple-100 text-purple-800',
    verified: 'bg-emerald-100 text-emerald-800',
    rejected: 'bg-red-100 text-red-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    in_progress: 'En progreso',
    cleaned: 'Limpiado',
    pending_review: 'Pendiente de revisión',
    verified: 'Verificado',
    rejected: 'Rechazado',
  }
  return labels[status] || status
}

export function getRedemptionStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    processing: 'Procesando',
    activated: 'Activado',
    shipped: 'Enviado',
    delivered: 'Entregado',
    cancelled: 'Cancelado',
  }
  return labels[status] || status
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const UPLOADS_BASE = API_BASE.replace('/api/v1', '')

export function resolveImageUrl(url: string | null | undefined): string | null {
  if (!url) return null
  if (url.startsWith('http://') || url.startsWith('https://')) return url
  return `${UPLOADS_BASE}${url}`
}

