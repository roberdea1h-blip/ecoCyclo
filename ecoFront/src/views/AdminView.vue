<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/authStore'
import AppLayout from '../components/shared/AppLayout.vue'

import AdminUsersTab from '../components/admin/AdminUsersTab.vue'
import AdminReportsTab from '../components/admin/AdminReportsTab.vue'
import AdminRewardsTab from '../components/admin/AdminRewardsTab.vue'
import AdminWasteTypesTab from '../components/admin/AdminWasteTypesTab.vue'
import AdminRedemptionsTab from '../components/admin/AdminRedemptionsTab.vue'
import AdminSetupTab from '../components/admin/AdminSetupTab.vue'

const authStore = useAuthStore()
const activeTab = ref<'users' | 'reports' | 'rewards' | 'waste-types' | 'redemptions' | 'setup'>('users')
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

      <AdminUsersTab v-if="activeTab === 'users'" />
      <AdminReportsTab v-if="activeTab === 'reports'" />
      <AdminRewardsTab v-if="activeTab === 'rewards'" />
      <AdminWasteTypesTab v-if="activeTab === 'waste-types'" />
      <AdminRedemptionsTab v-if="activeTab === 'redemptions'" />
      <AdminSetupTab v-if="activeTab === 'setup'" />
    </div>
  </AppLayout>
</template>
