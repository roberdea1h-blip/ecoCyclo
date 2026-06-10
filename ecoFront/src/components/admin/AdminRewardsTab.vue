<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi } from '../../api/admin'
import { useRewardStore } from '../../stores/rewardStore'
import { formatPoints, resolveImageUrl } from '../../utils/format'
import type { Reward } from '../../types'
import BaseBadge from '../base/BaseBadge.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSpinner from '../base/BaseSpinner.vue'
import IconGift from '../icons/IconGift.vue'
import AdminCreateRewardModal from '../modals/AdminCreateRewardModal.vue'
import AdminEditRewardModal from '../modals/AdminEditRewardModal.vue'

const rewardStore = useRewardStore()
const loading = ref(false)
const error = ref<string | null>(null)

const showCreateReward = ref(false)
const rewardCreated = ref(false)

const showEditRewardModal = ref(false)
const editingReward = ref<Reward | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    await rewardStore.fetchRewards()
  } finally {
    loading.value = false
  }
})

function openCreateReward() {
  rewardCreated.value = false
  showCreateReward.value = true
}

async function handleCreateReward(data: { data: { name: string; description: string; points_cost: number; stock: number }; imageFile: File | null }) {
  try {
    const reward = await adminApi.createReward(data.data)
    if (data.imageFile) {
      const formData = new FormData()
      formData.append('file', data.imageFile)
      await adminApi.uploadRewardImage(reward.id, formData)
    }
    await rewardStore.fetchRewards()
    rewardCreated.value = true
  } catch (e: any) {
    error.value = e.message || 'Error al crear recompensa'
  }
}

function openEditReward(r: Reward) {
  editingReward.value = r
  showEditRewardModal.value = true
}

async function handleSaveReward(data: { name: string; description: string; points_cost: number; stock: number }) {
  if (!editingReward.value) return
  try {
    const updated = await adminApi.updateReward(editingReward.value.id, data)
    const idx = rewardStore.rewards.findIndex(r => r.id === editingReward.value!.id)
    if (idx !== -1) rewardStore.rewards[idx] = updated
    showEditRewardModal.value = false
  } catch (e: any) {
    error.value = e.message || 'Error al actualizar recompensa'
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

    <AdminCreateRewardModal
      :show="showCreateReward"
      :reward-created="rewardCreated"
      @update:show="showCreateReward = $event"
      @save="handleCreateReward"
    />

    <AdminEditRewardModal
      :show="showEditRewardModal"
      :reward="editingReward"
      @update:show="showEditRewardModal = $event"
      @save="handleSaveReward"
    />
  </div>
</template>
