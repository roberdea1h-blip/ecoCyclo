<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../api/admin'
import { useAuthStore } from '../stores/authStore'
import { useFormValidation } from '../composables/useFormValidation'
import { rewardSchema } from '../utils/validators'
import { getStatusLabel, formatDate, formatPoints } from '../utils/format'
import type { User, Report, Reward, WasteType, WasteTypeCreate, WasteTypeUpdate } from '../types'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseTextarea from '../components/base/BaseTextarea.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import BaseModal from '../components/base/BaseModal.vue'
import { useRewardStore } from '../stores/rewardStore'

const authStore = useAuthStore()
const rewardStore = useRewardStore()

const users = ref<User[]>([])
const adminReports = ref<Report[]>([])
const wasteTypes = ref<WasteType[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// Reward creation
const showCreateReward = ref(false)
const rewardForm = ref({ name: '', description: '', points_cost: 0, stock: 0 })
const { errors: rewardErrors, validate: validateReward } = useFormValidation(rewardSchema)
const creatingReward = ref(false)
const rewardCreated = ref(false)

// Setup
const setupLoading = ref(false)
const setupResult = ref<string | null>(null)

// Waste types
const showWasteTypeModal = ref(false)
const editingWasteType = ref<WasteType | null>(null)
const wasteTypeForm = ref<WasteTypeCreate>({ name: '', description: '', icon: '', points_per_report: 10 })
const savingWasteType = ref(false)

const activeTab = ref<'users' | 'reports' | 'rewards' | 'waste-types' | 'setup'>('users')

onMounted(async () => {
  if (!authStore.isAdmin) return
  await loadData()
})

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [usersData, reportsData, wasteTypesData] = await Promise.all([
      adminApi.users(),
      adminApi.reports(),
      adminApi.wasteTypes(),
      rewardStore.fetchRewards(),
    ])
    users.value = usersData
    adminReports.value = reportsData
    wasteTypes.value = wasteTypesData
  } catch (e: any) {
    error.value = e.message || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
}

function openCreateReward() {
  rewardForm.value = { name: '', description: '', points_cost: 0, stock: 0 }
  rewardCreated.value = false
  showCreateReward.value = true
}

async function handleCreateReward() {
  rewardForm.value.points_cost = Number(rewardForm.value.points_cost) || 0
  rewardForm.value.stock = Number(rewardForm.value.stock) || 0
  if (!validateReward(rewardForm.value)) return
  creatingReward.value = true
  try {
    await adminApi.createReward(rewardForm.value)
    rewardCreated.value = true
  } catch (e: any) {
    error.value = e.message || 'Error al crear recompensa'
  } finally {
    creatingReward.value = false
  }
}

// Waste type handlers
function openCreateWasteType() {
  editingWasteType.value = null
  wasteTypeForm.value = { name: '', description: '', icon: '', points_per_report: 10 }
  showWasteTypeModal.value = true
}

function openEditWasteType(wt: WasteType) {
  editingWasteType.value = wt
  wasteTypeForm.value = {
    name: wt.name,
    description: wt.description || '',
    icon: wt.icon || '',
    points_per_report: wt.points_per_report,
  }
  showWasteTypeModal.value = true
}

async function handleSaveWasteType() {
  if (!wasteTypeForm.value.name.trim()) return
  savingWasteType.value = true
  try {
    if (editingWasteType.value) {
      const updated = await adminApi.updateWasteType(editingWasteType.value.id, wasteTypeForm.value)
      const idx = wasteTypes.value.findIndex(w => w.id === editingWasteType.value!.id)
      if (idx !== -1) wasteTypes.value[idx] = updated
    } else {
      const created = await adminApi.createWasteType(wasteTypeForm.value)
      wasteTypes.value.push(created)
    }
    showWasteTypeModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al guardar tipo de residuo'
  } finally {
    savingWasteType.value = false
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

async function handleSetup() {
  if (!confirm('¿Ejecutar setup inicial? Esto puede crear datos iniciales en el sistema.')) return
  setupLoading.value = true
  setupResult.value = null
  try {
    const result = await adminApi.setup()
    setupResult.value = result.message || 'Setup completado'
    await loadData()
  } catch (e: any) {
    setupResult.value = e.message || 'Error en setup'
  } finally {
    setupLoading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <div class="space-y-6" v-if="!authStore.isAdmin">
      <div class="text-center py-12">
        <p class="text-lg text-gray-500">No tienes permisos de administrador</p>
      </div>
    </div>

    <div class="space-y-6" v-else>
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Administración</h1>
        <p class="text-gray-600 mt-1">Panel de administración del sistema</p>
      </div>

      <BaseAlert v-if="error" variant="error" dismissible @dismiss="error = null">
        {{ error }}
      </BaseAlert>

      <div class="flex gap-2 border-b border-gray-200">
        <button
          v-for="tab in [{ id: 'users', label: 'Usuarios' }, { id: 'reports', label: 'Reportes' }, { id: 'rewards', label: 'Recompensas' }, { id: 'waste-types', label: 'Residuos' }, { id: 'setup', label: 'Setup' }]"
          :key="tab.id"
          class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
          :class="activeTab === tab.id ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          @click="activeTab = tab.id as typeof activeTab"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'">
        <BaseSpinner v-if="loading" size="md" />
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
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Reports Tab -->
      <div v-if="activeTab === 'reports'">
        <BaseSpinner v-if="loading" size="md" />
        <div v-else class="space-y-3">
          <div v-for="r in adminReports" :key="r.id" class="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-200">
            <div class="min-w-0">
              <router-link :to="`/reports/${r.id}`" class="text-sm font-medium text-gray-900 hover:text-emerald-600">
                {{ r.title }}
              </router-link>
              <p class="text-xs text-gray-500 mt-0.5">{{ r.user_name }} - {{ formatDate(r.created_at) }}</p>
            </div>
            <BaseBadge
              size="sm"
              :variant="r.status === 'cleaned' ? 'success' : r.status === 'pending' ? 'warning' : 'info'"
            >
              {{ getStatusLabel(r.status) }}
            </BaseBadge>
          </div>
        </div>
      </div>

      <!-- Rewards Tab -->
      <div v-if="activeTab === 'rewards'">
        <div class="flex justify-end mb-4">
          <BaseButton @click="openCreateReward">Crear recompensa</BaseButton>
        </div>
        <BaseSpinner v-if="loading" size="md" />
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="r in rewardStore.rewards" :key="r.id" class="p-4 bg-white rounded-lg border border-gray-200">
            <h3 class="font-semibold text-gray-900">{{ r.name }}</h3>
            <p class="text-sm text-gray-600 mt-1">{{ r.description }}</p>
            <div class="flex items-center justify-between mt-2 text-sm">
              <span class="font-medium text-emerald-600">{{ formatPoints(r.points_cost) }} pts</span>
              <span class="text-gray-500">Stock: {{ r.stock }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Waste Types Tab -->
      <div v-if="activeTab === 'waste-types'">
        <div class="flex justify-end mb-4">
          <BaseButton @click="openCreateWasteType">Crear tipo de residuo</BaseButton>
        </div>
        <BaseSpinner v-if="loading" size="md" />
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
      </div>

      <!-- Setup Tab -->
      <div v-if="activeTab === 'setup'">
        <BaseCard>
          <h2 class="text-lg font-semibold text-gray-900 mb-2">Setup inicial</h2>
          <p class="text-sm text-gray-600 mb-4">Ejecuta la configuración inicial del sistema para crear datos por defecto.</p>
          <BaseButton :loading="setupLoading" @click="handleSetup">Ejecutar setup</BaseButton>
          <BaseAlert v-if="setupResult" :variant="setupResult.includes('Error') ? 'error' : 'success'" class="mt-4">
            {{ setupResult }}
          </BaseAlert>
        </BaseCard>
      </div>
    </div>

    <BaseModal v-model="showCreateReward" title="Crear recompensa">
      <div v-if="rewardCreated" class="text-center py-6">
        <span class="text-4xl">✅</span>
        <p class="text-lg font-semibold text-gray-900 mt-3">Recompensa creada</p>
        <BaseButton class="mt-4" @click="showCreateReward = false">Cerrar</BaseButton>
      </div>
      <form v-else @submit.prevent="handleCreateReward" class="space-y-4">
        <BaseInput
          v-model="rewardForm.name"
          label="Nombre"
          required
          :error="rewardErrors.name"
        />
        <BaseTextarea
          v-model="rewardForm.description"
          label="Descripción"
          required
          :error="rewardErrors.description"
        />
        <BaseInput
          v-model="rewardForm.points_cost"
          label="Costo en puntos"
          type="number"
          required
          :error="rewardErrors.points_cost"
        />
        <BaseInput
          v-model="rewardForm.stock"
          label="Stock"
          type="number"
          required
          :error="rewardErrors.stock"
        />
        <div class="flex gap-3">
          <BaseButton type="submit" :loading="creatingReward">Crear</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showCreateReward = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal v-model="showWasteTypeModal" :title="editingWasteType ? 'Editar tipo de residuo' : 'Crear tipo de residuo'">
      <form @submit.prevent="handleSaveWasteType" class="space-y-4">
        <BaseInput
          v-model="wasteTypeForm.name"
          label="Nombre"
          placeholder="Ej: Plástico"
          required
        />
        <BaseInput
          v-model="wasteTypeForm.description"
          label="Descripción"
          placeholder="Breve descripción del tipo de residuo"
        />
        <BaseInput
          v-model="wasteTypeForm.icon"
          label="Icono"
          placeholder="Identificador del icono"
        />
        <BaseInput
          v-model.number="wasteTypeForm.points_per_report"
          label="Puntos por reporte"
          type="number"
          min="0"
        />
        <div class="flex gap-3">
          <BaseButton type="submit" :loading="savingWasteType">
            {{ editingWasteType ? 'Guardar' : 'Crear' }}
          </BaseButton>
          <BaseButton type="button" variant="secondary" @click="showWasteTypeModal = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

