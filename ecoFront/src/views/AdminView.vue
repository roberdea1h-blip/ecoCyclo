<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../api/admin'
import { reportsApi } from '../api/reports'
import { useAuthStore } from '../stores/authStore'
import { useFormValidation } from '../composables/useFormValidation'
import { rewardSchema } from '../utils/validators'
import { getStatusLabel, getRedemptionStatusLabel, formatDate, formatPoints, resolveImageUrl } from '../utils/format'
import type { Redemption, User, Report, Reward, WasteType, WasteTypeCreate, WasteTypeUpdate } from '../types'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseSelect from '../components/base/BaseSelect.vue'
import BaseTextarea from '../components/base/BaseTextarea.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseImageUpload from '../components/base/BaseImageUpload.vue'
import { useRewardStore } from '../stores/rewardStore'
import IconGift from '../components/icons/IconGift.vue'

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
const rewardImageFile = ref<File | null>(null)
const uploadingImage = ref(false)

// Reward editing
const showEditRewardModal = ref(false)
const editingReward = ref<Reward | null>(null)
const editRewardForm = ref({ name: '', description: '', points_cost: 0, stock: 0 })
const savingReward = ref(false)

// Report editing
const showEditReportModal = ref(false)
const editingReport = ref<Report | null>(null)
const editReportForm = ref({ title: '', description: '', address: '', estimated_quantity: null as number | null, status: '' })

// Setup
const setupLoading = ref(false)
const setupResult = ref<string | null>(null)

// Waste types
const showWasteTypeModal = ref(false)
const editingWasteType = ref<WasteType | null>(null)
const wasteTypeForm = ref<WasteTypeCreate>({ name: '', description: '', icon: '', points_per_report: 10 })
const savingWasteType = ref(false)

const redemptions = ref<Redemption[]>([])
const redemptionStatusUpdating = ref<string | null>(null)
const activeTab = ref<'users' | 'reports' | 'rewards' | 'waste-types' | 'redemptions' | 'setup'>('users')

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

async function fetchRedemptions() {
  loading.value = true
  error.value = null
  try {
    redemptions.value = await adminApi.redemptions()
  } catch (e: any) {
    error.value = e.message || 'Error al cargar canjes'
  } finally {
    loading.value = false
  }
}

async function handleUpdateRedemptionStatus(id: string, status: string) {
  redemptionStatusUpdating.value = id
  try {
    const updated = await adminApi.updateRedemptionStatus(id, { status })
    const idx = redemptions.value.findIndex(r => r.id === id)
    if (idx !== -1) redemptions.value[idx] = updated
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar estado del canje'
  } finally {
    redemptionStatusUpdating.value = null
  }
}

function openCreateReward() {
  rewardForm.value = { name: '', description: '', points_cost: 0, stock: 0 }
  rewardCreated.value = false
  rewardImageFile.value = null
  showCreateReward.value = true
}

async function handleCreateReward() {
  rewardForm.value.points_cost = Number(rewardForm.value.points_cost) || 0
  rewardForm.value.stock = Number(rewardForm.value.stock) || 0
  if (!validateReward(rewardForm.value)) return
  creatingReward.value = true
  try {
    const reward = await adminApi.createReward(rewardForm.value)

    if (rewardImageFile.value) {
      uploadingImage.value = true
      const formData = new FormData()
      formData.append('file', rewardImageFile.value)
      await adminApi.uploadRewardImage(reward.id, formData)
    }

    await rewardStore.fetchRewards()
    rewardCreated.value = true
  } catch (e: any) {
    error.value = e.message || 'Error al crear recompensa'
  } finally {
    creatingReward.value = false
    uploadingImage.value = false
  }
}

// Reward edit/delete handlers
function openEditReward(r: Reward) {
  editingReward.value = r
  editRewardForm.value = {
    name: r.name,
    description: r.description,
    points_cost: r.points_cost,
    stock: r.stock ?? 0,
  }
  showEditRewardModal.value = true
}

async function handleSaveReward() {
  if (!editingReward.value) return
  savingReward.value = true
  try {
    const updated = await adminApi.updateReward(editingReward.value.id, editRewardForm.value)
    const idx = rewardStore.rewards.findIndex(r => r.id === editingReward.value!.id)
    if (idx !== -1) rewardStore.rewards[idx] = updated
    showEditRewardModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar recompensa'
  } finally {
    savingReward.value = false
  }
}

async function handleDeleteReward(id: string) {
  if (!confirm('¿Eliminar esta recompensa?')) return
  try {
    await adminApi.deleteReward(id)
    rewardStore.rewards = rewardStore.rewards.filter(r => r.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar recompensa'
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

async function handleDeleteUser(id: string) {
  if (!confirm('¿Eliminar este usuario? Todos sus datos (reportes, notificaciones, etc.) serán eliminados permanentemente.')) return
  try {
    await adminApi.deleteUser(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar usuario'
  }
}

async function handleAdminDeleteReport(id: string) {
  if (!confirm('¿Eliminar este reporte?')) return
  try {
    await reportsApi.delete(id)
    adminReports.value = adminReports.value.filter(r => r.id !== id)
  } catch (e: any) {
    error.value = e.message || 'Error al eliminar reporte'
  }
}

function openAdminEditReport(r: Report) {
  editingReport.value = r
  editReportForm.value = {
    title: r.title,
    description: r.description || '',
    address: r.address || '',
    estimated_quantity: r.estimated_quantity,
    status: r.status,
  }
  showEditReportModal.value = true
}

async function handleAdminEditReport() {
  if (!editingReport.value) return
  try {
    const updated = await reportsApi.update(editingReport.value.id, editReportForm.value)
    const idx = adminReports.value.findIndex(r => r.id === editingReport.value!.id)
    if (idx !== -1) adminReports.value[idx] = updated
    showEditReportModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar reporte'
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
          v-for="tab in [{ id: 'users', label: 'Usuarios' }, { id: 'reports', label: 'Reportes' }, { id: 'rewards', label: 'Recompensas' }, { id: 'waste-types', label: 'Residuos' }, { id: 'redemptions', label: 'Canjes' }, { id: 'setup', label: 'Setup' }]"
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
            </tbody>
          </table>
        </div>
      </div>

      <!-- Reports Tab -->
      <div v-if="activeTab === 'reports'">
        <BaseSpinner v-if="loading" size="md" />
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
              <tr v-for="r in adminReports" :key="r.id" class="border-b border-gray-100">
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
                    <BaseButton variant="secondary" size="sm" @click="openAdminEditReport(r)">Editar</BaseButton>
                    <BaseButton variant="danger" size="sm" @click="handleAdminDeleteReport(r.id)">Eliminar</BaseButton>
                  </div>
                </td>
              </tr>
              <tr v-if="adminReports.length === 0">
                <td colspan="5" class="py-8 text-center text-gray-400">
                  No hay reportes.
                </td>
              </tr>
            </tbody>
          </table>
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
            <div class="w-full h-36 bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
              <img v-if="r.image_url" :src="resolveImageUrl(r.image_url)" :alt="r.name" class="w-full h-full object-cover" />
              <span v-else class="text-gray-400 text-3xl">
                <IconGift class="w-12 h-12" />
              </span>
            </div>
            <h3 class="font-semibold text-gray-900">{{ r.name }}</h3>
            <p class="text-sm text-gray-600 mt-1">{{ r.description }}</p>
            <div class="flex items-center justify-between mt-2 text-sm">
              <span class="font-medium text-emerald-600">{{ formatPoints(r.points_cost) }} pts</span>
              <span class="text-gray-500">Stock: {{ r.stock }}</span>
            </div>
            <div class="flex gap-2 mt-3">
              <BaseButton variant="secondary" size="sm" class="flex-1" @click="openEditReward(r)">Editar</BaseButton>
              <BaseButton variant="danger" size="sm" class="flex-1" @click="handleDeleteReward(r.id)">Eliminar</BaseButton>
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

      <!-- Redemptions Tab -->
      <div v-if="activeTab === 'redemptions'">
        <BaseSpinner v-if="loading" size="md" />
        <div v-else class="overflow-x-auto">
          <div class="flex justify-end mb-4">
            <BaseButton variant="secondary" size="sm" @click="fetchRedemptions">Actualizar</BaseButton>
          </div>
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 text-left text-gray-500">
                <th class="pb-3 font-medium">ID</th>
                <th class="pb-3 font-medium">Usuario</th>
                <th class="pb-3 font-medium">Recompensa</th>
                <th class="pb-3 font-medium">Puntos</th>
                <th class="pb-3 font-medium">Estado</th>
                <th class="pb-3 font-medium">Fecha</th>
                <th class="pb-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in redemptions" :key="r.id" class="border-b border-gray-100">
                <td class="py-3 text-gray-500 text-xs">{{ r.id }}</td>
                <td class="py-3 font-medium text-gray-900">{{ r.user_id }}</td>
                <td class="py-3 text-gray-600">{{ r.reward_id }}</td>
                <td class="py-3">{{ formatPoints(r.points_spent) }}</td>
                <td class="py-3">
                  <BaseBadge
                    size="sm"
                    :variant="r.status === 'delivered' ? 'success' : r.status === 'cancelled' ? 'danger' : 'info'"
                  >
                    {{ getRedemptionStatusLabel(r.status) }}
                  </BaseBadge>
                </td>
                <td class="py-3 text-gray-500">{{ formatDate(r.redeemed_at) }}</td>
                <td class="py-3">
                  <div class="flex gap-2">
                    <BaseSelect
                      :model-value="r.status"
                      :options="[
                        { value: 'pending', label: 'Pendiente' },
                        { value: 'processing', label: 'Procesando' },
                        { value: 'activated', label: 'Activado' },
                        { value: 'shipped', label: 'Enviado' },
                        { value: 'delivered', label: 'Entregado' },
                        { value: 'cancelled', label: 'Cancelado' },
                      ]"
                      :disabled="redemptionStatusUpdating === r.id"
                      @update:model-value="(val: string) => handleUpdateRedemptionStatus(r.id, val)"
                    />
                  </div>
                </td>
              </tr>
              <tr v-if="redemptions.length === 0">
                <td colspan="7" class="py-8 text-center text-gray-400">
                  No hay canjes registrados.
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
        <BaseImageUpload v-model="rewardImageFile" label="Imagen" />
        <div class="flex gap-3">
          <BaseButton type="submit" :loading="creatingReward || uploadingImage">Crear</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showCreateReward = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal v-model="showEditRewardModal" title="Editar recompensa">
      <form @submit.prevent="handleSaveReward" class="space-y-4">
        <BaseInput
          v-model="editRewardForm.name"
          label="Nombre"
          required
        />
        <BaseTextarea
          v-model="editRewardForm.description"
          label="Descripción"
          required
        />
        <BaseInput
          v-model.number="editRewardForm.points_cost"
          label="Costo en puntos"
          type="number"
          required
        />
        <BaseInput
          v-model.number="editRewardForm.stock"
          label="Stock"
          type="number"
          required
        />
        <div class="flex gap-3">
          <BaseButton type="submit" :loading="savingReward">Guardar</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showEditRewardModal = false">Cancelar</BaseButton>
        </div>
      </form>
    </BaseModal>

    <BaseModal v-model="showEditReportModal" title="Editar reporte">
      <form @submit.prevent="handleAdminEditReport" class="space-y-4">
        <BaseInput
          v-model="editReportForm.title"
          label="Título"
          required
        />
        <BaseTextarea
          v-model="editReportForm.description"
          label="Descripción"
        />
        <BaseInput
          v-model="editReportForm.address"
          label="Dirección"
        />
        <BaseInput
          v-model.number="editReportForm.estimated_quantity"
          label="Cantidad estimada (kg)"
          type="number"
          min="0"
          step="0.1"
        />
        <BaseSelect
          v-model="editReportForm.status"
          label="Estado"
          :options="[
            { value: 'pending', label: 'Pendiente' },
            { value: 'in_progress', label: 'En progreso' },
            { value: 'pending_review', label: 'Pendiente de revisión' },
            { value: 'verified', label: 'Verificado' },
            { value: 'rejected', label: 'Rechazado' },
            { value: 'cleaned', label: 'Limpiado' },
          ]"
        />
        <div class="flex gap-3">
          <BaseButton type="submit">Guardar</BaseButton>
          <BaseButton type="button" variant="secondary" @click="showEditReportModal = false">Cancelar</BaseButton>
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

