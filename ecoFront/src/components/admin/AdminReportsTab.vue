<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import { reportsApi } from '../../api/reports'
import { getStatusLabel, formatDate } from '../../utils/format'
import type { Report } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseInput from '../base/BaseInput.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseSelect from '../base/BaseSelect.vue'
import BaseSpinner from '../base/BaseSpinner.vue'
import BaseModal from '../base/BaseModal.vue'

const reports = ref<Report[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const showEditModal = ref(false)
const editingReport = ref<Report | null>(null)
const editForm = ref({ title: '', description: '', address: '', estimated_quantity: null as number | null, status: '' })

const statusOptions = [
  { value: 'pending', label: 'Pendiente' },
  { value: 'in_progress', label: 'En progreso' },
  { value: 'pending_review', label: 'Pendiente de revisión' },
  { value: 'verified', label: 'Verificado' },
  { value: 'rejected', label: 'Rechazado' },
  { value: 'cleaned', label: 'Limpiado' },
]

onMounted(async () => {
  loading.value = true
  try {
    reports.value = await adminApi.reports()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar reportes'
  } finally {
    loading.value = false
  }
})

function openEdit(r: Report) {
  editingReport.value = r
  editForm.value = {
    title: r.title,
    description: r.description || '',
    address: r.address || '',
    estimated_quantity: r.estimated_quantity,
    status: r.status,
  }
  showEditModal.value = true
}

async function handleEdit() {
  if (!editingReport.value) return
  try {
    const updated = await reportsApi.update(editingReport.value.id, editForm.value)
    const idx = reports.value.findIndex(r => r.id === editingReport.value!.id)
    if (idx !== -1) reports.value[idx] = updated
    showEditModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar reporte'
  }
}

async function handleDelete(id: string) {
  if (!confirm('¿Eliminar este reporte?')) return
  try {
    await reportsApi.delete(id)
    reports.value = reports.value.filter(r => r.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar reporte'
  }
}
</script>

<template>
  <div>
    <BaseSpinner v-if="loading" size="md" />
    <p v-else-if="error" class="text-red-600 text-sm">{{ error }}</p>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 text-left text-gray-500">
            <th class="pb-3 font-medium">Título</th>
            <th class="pb-3 font-medium">Usuario</th>
            <th class="pb-3 font-medium">Estado</th>
            <th class="pb-3 font-medium">Fecha</th>
            <th class="pb-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in reports" :key="r.id" class="border-b border-gray-100">
            <td class="py-3">
              <router-link :to="`/reports/${r.id}`" class="font-medium text-gray-900 hover:text-emerald-600">
                {{ r.title }}
              </router-link>
            </td>
            <td class="py-3 text-gray-600">{{ r.user_name }}</td>
            <td class="py-3">
              <BaseBadge
                size="sm"
                :variant="r.status === 'verified' || r.status === 'cleaned' ? 'success' : r.status === 'rejected' ? 'danger' : r.status === 'pending' || r.status === 'pending_review' ? 'warning' : 'info'"
              >
                {{ getStatusLabel(r.status) }}
              </BaseBadge>
            </td>
            <td class="py-3 text-gray-500">{{ formatDate(r.created_at) }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <BaseButton variant="secondary" size="sm" @click="openEdit(r)">Editar</BaseButton>
                <BaseButton variant="danger" size="sm" @click="handleDelete(r.id)">Eliminar</BaseButton>
              </div>
            </td>
          </tr>
          <tr v-if="reports.length === 0">
            <td colspan="5" class="py-8 text-center text-gray-400">
              No hay reportes.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal v-model="showEditModal" title="Editar reporte">
      <form @submit.prevent="handleEdit" class="space-y-4">
        <BaseInput
          v-model="editForm.title"
          label="Título"
          required
        />
        <BaseTextarea
          v-model="editForm.description"
          label="Descripción"
        />
        <BaseInput
          v-model="editForm.address"
          label="Dirección"
        />
        <BaseInput
          v-model.number="editForm.estimated_quantity"
          label="Cantidad estimada (kg)"
          type="number"
          min="0"
          step="0.1"
        />
        <BaseSelect
          v-model="editForm.status"
          label="Estado"
          :options="statusOptions"
        />
        <div class="flex gap-3">
          <BaseButton type="submit">Guardar</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showEditModal = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>
  </div>
</template>
