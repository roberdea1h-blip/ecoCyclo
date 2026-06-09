import { reactive } from 'vue'
import type { ZodSchema, ZodError } from 'zod'

export function useFormValidation<T extends Record<string, unknown>>(schema: ZodSchema<T>) {
  const errors = reactive<Record<string, string>>({})

  function validate(data: Record<string, unknown>): data is T {
    const result = schema.safeParse(data)

    for (const key of Object.keys(errors)) {
      delete errors[key]
    }

    if (result.success) {
      return true
    }

    const zodError = result.error as ZodError
    for (const issue of zodError.issues) {
      const path = issue.path.join('.')
      if (path) {
        errors[path] = issue.message
      }
    }
    return false
  }

  function clearErrors() {
    for (const key of Object.keys(errors)) {
      delete errors[key]
    }
  }

  return { errors, validate, clearErrors }
}
