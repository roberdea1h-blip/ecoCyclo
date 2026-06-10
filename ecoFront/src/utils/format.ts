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
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    in_progress: 'En progreso',
    cleaned: 'Limpiado',
  }
  return labels[status] || status
}

