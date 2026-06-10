import { ref, type Ref } from 'vue'
import { isApiError, type ApiError } from '../types/api-error'

const errorMessages: Record<string, string> = {
  // users
  user_not_found: 'Usuario no encontrado.',
  email_already_exists: 'El correo electrónico ya está registrado.',
  invalid_credentials: 'Correo o contraseña incorrectos.',
  invalid_role: 'Rol de usuario inválido.',
  user_not_active: 'La cuenta de usuario no está activa.',
  username_already_exists: 'El nombre de usuario ya está registrado.',
  cannot_delete_self: 'No puedes eliminar tu propio usuario.',

  // auth
  unauthorized: 'No autorizado. Inicia sesión nuevamente.',
  session_expired: 'Sesión expirada. Inicia sesión nuevamente.',

  // refresh_token
  refresh_token_not_found: 'Sesión inválida. Inicia sesión nuevamente.',
  refresh_token_expired: 'Sesión expirada. Inicia sesión nuevamente.',
  refresh_token_revoked: 'Sesión revocada. Inicia sesión nuevamente.',
  invalid_jti: 'Sesión inválida.',
  refresh_token_user_mismatch: 'La sesión no corresponde al usuario.',

  // report
  report_not_found: 'Reporte no encontrado.',
  invalid_waste_type_for_report: 'Tipo de residuo inválido para el reporte.',
  invalid_coordinates: 'Las coordenadas ingresadas no son válidas.',
  report_already_processed: 'El reporte ya fue procesado.',
  unauthorized_report_status_change: 'No tienes permiso para cambiar el estado del reporte.',
  report_not_pending: 'El reporte no está pendiente.',
  cannot_claim_own_report: 'No puedes reclamar tu propio reporte.',
  report_not_in_progress: 'El reporte no está en progreso.',
  not_assigned_cleaner: 'No eres el limpiador asignado a este reporte.',
  report_not_pending_review: 'El reporte no está esperando revisión.',
  not_original_reporter: 'Solo el creador del reporte puede realizar esta acción.',

  // reward
  reward_not_found: 'Recompensa no encontrada.',
  reward_inactive: 'La recompensa no está disponible.',
  invalid_reward_points_value: 'Valor de puntos inválido para la recompensa.',
  negative_stock: 'El stock no puede ser negativo.',

  // redemption
  redemption_not_found: 'Canje no encontrado.',
  insufficient_points_for_redemption: 'No tienes suficientes puntos para canjear.',
  reward_out_of_stock: 'La recompensa está agotada.',
  redemption_already_processed: 'El canje ya fue procesado.',
  user_not_eligible_for_redemption: 'No eres elegible para este canje.',

  // point_transaction
  insufficient_points: 'Puntos insuficientes.',
  duplicate_transaction: 'Transacción duplicada.',
  invalid_transaction_type: 'Tipo de transacción inválido.',
  points_overflow: 'El saldo de puntos excede el límite permitido.',
  point_transaction_not_found: 'Transacción no encontrada.',

  // notification
  notification_not_found: 'Notificación no encontrada.',
  notification_target_user_not_found: 'Usuario destino no encontrado.',
  invalid_notification_type: 'Tipo de notificación inválido.',
  notification_delivery_failed: 'Error al enviar la notificación.',

  // role
  role_not_found: 'Rol no encontrado.',
  role_name_already_exists: 'El nombre del rol ya existe.',
  role_in_use: 'El rol está en uso y no puede eliminarse.',
  system_role_not_modifiable: 'El rol de sistema no puede modificarse.',

  // waste_type
  waste_type_not_found: 'Tipo de residuo no encontrado.',
  waste_type_name_already_exists: 'El nombre del tipo de residuo ya existe.',
  waste_type_in_use: 'El tipo de residuo está en uso.',
  invalid_unit_of_measure: 'Unidad de medida inválida.',

  // report_image
  report_image_not_found: 'Imagen no encontrada.',
  report_for_image_not_found: 'Reporte asociado a la imagen no encontrado.',
  invalid_image_mime_type: 'El tipo de archivo de imagen no es válido.',
  image_size_exceeded: 'La imagen excede el tamaño máximo permitido.',
  report_image_limit_exceeded: 'Límite de imágenes por reporte excedido.',

  // generic
  validation_error: 'Datos inválidos. Revisa los campos del formulario.',
  internal_server_error: 'Error del servidor. Intenta de nuevo más tarde.',
  not_found: 'Recurso no encontrado.',
  conflict: 'Conflicto al procesar la solicitud.',
  forbidden: 'No tienes permiso para realizar esta acción.',
  business_rule: 'La operación no pudo completarse.',
}

export function useApiError() {
  const errorMessage = ref<string | null>(null) as Ref<string | null>

  function handleError(error: unknown): string {
    if (isApiError(error)) {
      const msg = errorMessages[error.error_code]
      if (msg) return msg
      return error.message || 'Error inesperado. Intenta de nuevo.'
    }
    if (error instanceof Error) {
      return error.message || 'Error inesperado. Intenta de nuevo.'
    }
    return 'Error inesperado. Intenta de nuevo.'
  }

  function setError(msg: string | null) {
    errorMessage.value = msg
  }

  function clearError() {
    errorMessage.value = null
  }

  return {
    errorMessage,
    handleError,
    setError,
    clearError,
  }
}
