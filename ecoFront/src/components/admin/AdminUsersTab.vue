<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import { useAuthStore } from '../../stores/authStore'
import { formatPoints } from '../../utils/format'
import type { User } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSpinner from '../base/BaseSpinner.vue'

const authStore = useAuthStore()
const users = ref<User[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    users.value = await adminApi.users()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar usuarios'
  } finally {
    loading.value = false
  }
})

async function handleDeleteUser(id: string) {
  if (!confirm('¿Eliminar este usuario? Todos sus datos (reportes, notificaciones, etc.) serán eliminados permanentemente.')) return
  try {
    await adminApi.deleteUser(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar usuario'
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
            <th class="pb-3 font-medium">ID</th>
            <th class="pb-3 font-medium">Nombre</th>
            <th class="pb-3 font-medium">Email</th>
            <th class="pb-3 font-medium">Rol</th>
            <th class="pb-3 font-medium">Puntos</th>
            <th class="pb-3 font-medium">Activo</th>
            <th class="pb-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" class="border-b border-gray-100">
            <td class="py-3 text-gray-500">{{ u.id }}</td>
            <td class="py-3 font-medium text-gray-900">{{ u.full_name }}</td>
            <td class="py-3 text-gray-600">{{ u.email }}</td>
            <td class="py-3">
              <BaseBadge :variant="u.role_name === 'admin' ? 'info' : 'default'" size="sm">
                {{ u.role_name }}
              </BaseBadge>
            </td>
            <td class="py-3">{{ formatPoints(u.points) }}</td>
            <td class="py-3">
              <span :class="u.is_active ? 'text-green-600' : 'text-red-600'">
                {{ u.is_active ? 'Sí' : 'No' }}
              </span>
            </td>
            <td class="py-3">
              <BaseButton
                v-if="u.id !== authStore.user?.id"
                variant="danger"
                size="sm"
                @click="handleDeleteUser(u.id)"
              >
                Eliminar
              </BaseButton>
            </td>
          </tr>
          <tr v-if="users.length === 0">
            <td colspan="7" class="py-8 text-center text-gray-400">
              No hay usuarios registrados.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
