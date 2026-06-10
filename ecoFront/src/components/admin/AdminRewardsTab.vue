<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import { useRewardStore } from '../../stores/rewardStore'
import { useFormValidation } from '../../composables/useFormValidation'
import { rewardSchema } from '../../utils/validators'
import { formatPoints, resolveImageUrl } from '../../utils/format'
import type { Reward } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseInput from '../base/BaseInput.vue'
import BaseTextarea from '../base/BaseTextarea.vue'
import BaseSpinner from '../base/BaseSpinner.vue'
import BaseModal from '../base/BaseModal.vue'
import BaseImageUpload from '../base/BaseImageUpload.vue'
import IconGift from '../icons/IconGift.vue'

const rewardStore = useRewardStore()
const loading = ref(false)
const error = ref<string | null>(null)

const showCreateReward = ref(false)
const rewardForm = ref({ name: '', description: '', points_cost: 0, stock: 0 })
const { errors: rewardErrors, validate: validateReward } = useFormValidation(rewardSchema)
const creatingReward = ref(false)
const rewardCreated = ref(false)
const rewardImageFile = ref<File | null>(null)
const uploadingImage = ref(false)

const showEditRewardModal = ref(false)
const editingReward = ref<Reward | null>(null)
const editRewardForm = ref({ name: '', description: '', points_cost: 0, stock: 0 })
const savingReward = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    await rewardStore.fetchRewards()
  } finally {
    loading.value = false
  }
})

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
</script>

<template>
  <div>
    <div class="flex justify-end mb-4">
      <BaseButton @click="openCreateReward">Crear recompensa</BaseButton>
    </div>
    <BaseSpinner v-if="loading" size="md" />
    <p v-else-if="error" class="text-red-600 text-sm">{{ error }}</p>
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
  </div>
</template>
