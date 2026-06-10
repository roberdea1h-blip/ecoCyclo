export interface ApiError {
  error_code: string
  message: string
  details?: unknown
}

export function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === 'object' &&
    value !== null &&
    'error_code' in value &&
    'message' in value
  )
}
