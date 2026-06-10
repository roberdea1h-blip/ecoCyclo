<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import type { WasteType, WasteTypeCreate } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSpinner from '../base/BaseSpinner.vue'
import AdminWasteTypeFormModal from '../modals/AdminWasteTypeFormModal.vue'

const wasteTypes = ref<WasteType[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const showWasteTypeModal = ref(false)
const editingWasteType = ref<WasteType | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    wasteTypes.value = await adminApi.wasteTypes()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar tipos de residuo'
  } finally {
    loading.value = false
  }
})

function openCreateWasteType() {
  editingWasteType.value = null
  showWasteTypeModal.value = true
}

function openEditWasteType(wt: WasteType) {
  editingWasteType.value = wt
  showWasteTypeModal.value = true
}

async function handleSaveWasteType(data: WasteTypeCreate) {
  try {
    if (editingWasteType.value) {
      const updated = await adminApi.updateWasteType(editingWasteType.value.id, data)
      const idx = wasteTypes.value.findIndex(w => w.id === editingWasteType.value!.id)
      if (idx !== -1) wasteTypes.value[idx] = updated
    } else {
      const created = await adminApi.createWasteType(data)
      wasteTypes.value.push(created)
    }
    showWasteTypeModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al guardar tipo de residuo'
  }
}

async function handleDeleteWasteType(id: string) {
  if (!confirm('¿Eliminar este tipo de residuo?')) return
  try {
    await adminApi.deleteWasteType(id)
    wasteTypes.value = wasteTypes.value.filter(w => w.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar tipo de residuo'
  }
}
</script>

<template>
  <div>
    <div class="flex justify-end mb-4">
      <BaseButton @click="openCreateWasteType">Crear tipo de residuo</BaseButton>
    </div>
    <BaseSpinner v-if="loading" size="md" />
    <p v-else-if="error" class="text-red-600 text-sm">{{ error }}</p>
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200 text-left text-gray-500">
            <th class="pb-3 font-medium">Nombre</th>
            <th class="pb-3 font-medium">Descripción</th>
            <th class="pb-3 font-medium">Icono</th>
            <th class="pb-3 font-medium">Puntos</th>
            <th class="pb-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="wt in wasteTypes" :key="wt.id" class="border-b border-gray-100">
            <td class="py-3 font-medium text-gray-900">{{ wt.name }}</td>
            <td class="py-3 text-gray-600 max-w-xs truncate">{{ wt.description }}</td>
            <td class="py-3 text-gray-500">{{ wt.icon }}</td>
            <td class="py-3">{{ wt.points_per_report }}</td>
            <td class="py-3">
              <div class="flex gap-2">
                <BaseButton variant="secondary" size="sm" @click="openEditWasteType(wt)">Editar</BaseButton>
                <BaseButton variant="danger" size="sm" @click="handleDeleteWasteType(wt.id)">Eliminar</BaseButton>
              </div>
            </td>
          </tr>
          <tr v-if="wasteTypes.length === 0">
            <td colspan="5" class="py-8 text-center text-gray-400">
              No hay tipos de residuo. Crea uno o ejecuta el Setup.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminWasteTypeFormModal
      :show="showWasteTypeModal"
      :waste-type="editingWasteType"
      @update:show="showWasteTypeModal = $event"
      @save="handleSaveWasteType"
    />
  </div>
</template>
