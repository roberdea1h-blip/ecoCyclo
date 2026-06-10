<script setup lang="ts">
import { formatPoints } from '../../utils/format'
import BaseCard from '../base/BaseCard.vue'
import IconStar from '../icons/IconStar.vue'
import IconReport from '../icons/IconReport.vue'
import IconBell from '../icons/IconBell.vue'

defineProps<{
  points: number
  totalReports: number
  verified: number
  unreadCount: number
}>()
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <BaseCard padding="md">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center shrink-0">
          <IconStar class="w-6 h-6 text-yellow-600" />
        </div>
        <div>
          <p class="text-sm text-gray-500">Puntos</p>
          <p class="text-xl font-bold text-gray-900">{{ formatPoints(points) }}</p>
        </div>
      </div>
    </BaseCard>

    <BaseCard padding="md">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
          <IconReport class="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <p class="text-sm text-gray-500">Mis reportes</p>
          <p class="text-xl font-bold text-gray-900">{{ totalReports }}</p>
        </div>
      </div>
    </BaseCard>

    <BaseCard padding="md">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center shrink-0">
          <IconReport class="w-6 h-6 text-green-600" />
        </div>
        <div>
          <p class="text-sm text-gray-500">Verificados</p>
          <p class="text-xl font-bold text-gray-900">{{ verified }}</p>
        </div>
      </div>
    </BaseCard>

    <BaseCard padding="md">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0">
          <IconBell class="w-6 h-6 text-red-600" />
        </div>
        <div>
          <p class="text-sm text-gray-500">No leídas</p>
          <p class="text-xl font-bold text-gray-900">{{ unreadCount }}</p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>
