import { api } from './http'
import type { WasteType } from '../types'

export const wasteTypesApi = {
  list() {
    return api.get<WasteType[]>('/waste-types')
  },
}
