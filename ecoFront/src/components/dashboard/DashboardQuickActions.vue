<script setup lang="ts">
import IconGift from '../icons/IconGift.vue'
import IconUser from '../icons/IconUser.vue'
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <router-link
      to="/reports/create"
      class="flex items-center justify-center gap-2 p-4 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors font-medium"
    >
      <span>+</span>
      Nuevo reporte
    </router-link>
    <router-link
      to="/rewards"
      class="flex items-center justify-center gap-2 p-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
    >
      <IconGift class="w-5 h-5" />
      Canjear puntos
    </router-link>
    <router-link
      to="/profile"
      class="flex items-center justify-center gap-2 p-4 bg-gray-700 text-white rounded-xl hover:bg-gray-800 transition-colors font-medium"
    >
      <IconUser class="w-5 h-5" />
      Mi perfil
    </router-link>
  </div>
</template>
