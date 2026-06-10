<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { usePointTransactionStore } from '../stores/pointTransactionStore'
import { useFormValidation } from '../composables/useFormValidation'
import { profileSchema } from '../utils/validators'
import { useApiError } from '../composables/useApiError'
import { formatPoints, formatDate } from '../utils/format'
import { api } from '../api/http'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseAlert from '../components/base/BaseAlert.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import ProfileReportHistory from '../components/profile/ProfileReportHistory.vue'
import IconStar from '../components/icons/IconStar.vue'

const authStore = useAuthStore()
const txStore = usePointTransactionStore()
const { errors, validate } = useFormValidation(profileSchema)
const { handleError } = useApiError()

const editing = ref(false)
const fullName = ref(authStore.user?.full_name || '')
const saveLoading = ref(false)
const saveError = ref<string | null>(null)
const saveSuccess = ref(false)

onMounted(async () => {
  await txStore.fetchTransactions()
})

async function handleSave() {
  const data = { full_name: fullName.value }
  if (!validate(data)) return
  saveLoading.value = true
  saveError.value = null
  saveSuccess.value = false
  try {
    const updated = await api.patch<any>('/users/me', data)
    if (authStore.user) {
      authStore.user.full_name = updated.full_name
    }
    saveSuccess.value = true
    editing.value = false
  } catch (e: unknown) {
    saveError.value = handleError(e)
  } finally {
    saveLoading.value = false
  }
}

function cancelEdit() {
  fullName.value = authStore.user?.full_name || ''
  editing.value = false
  saveError.value = null
  saveSuccess.value = false
}

function txBadgeVariant(type: string): 'success' | 'warning' | 'default' {
  if (type === 'earned') return 'success'
  if (type === 'redeemed') return 'warning'
  return 'default'
}

function txLabel(type: string): string {
  const labels: Record<string, string> = {
    earned: 'Ganados',
    redeemed: 'Canjeados',
    adjustment: 'Ajuste',
  }
  return labels[type] || type
}
</script>

<template>
  <AppLayout>
    <div class="max-w-3xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-gray-900">Mi perfil</h1>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-2 space-y-6">
          <BaseCard>
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900">Información personal</h2>
              <button
                v-if="!editing"
                class="text-sm text-emerald-600 hover:text-emerald-700 font-medium"
                @click="editing = true"
              >
                Editar
              </button>
            </div>

            <BaseAlert v-if="saveSuccess" variant="success" class="mb-4" dismissible @dismiss="saveSuccess = false">
              Perfil actualizado correctamente
            </BaseAlert>
            <BaseAlert v-if="saveError" variant="error" class="mb-4" dismissible @dismiss="saveError = null">
              {{ saveError }}
            </BaseAlert>

            <div v-if="!editing" class="space-y-3">
              <div>
                <span class="text-sm text-gray-500">Nombre completo</span>
                <p class="text-gray-900 font-medium">{{ authStore.user?.full_name || '-' }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-500">Correo electrónico</span>
                <p class="text-gray-900 font-medium">{{ authStore.user?.email || '-' }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-500">Usuario</span>
                <p class="text-gray-900 font-medium">{{ authStore.user?.username || '-' }}</p>
              </div>
              <div>
                <span class="text-sm text-gray-500">Rol</span>
                <p class="text-gray-900 font-medium capitalize">{{ authStore.user?.role_name || '-' }}</p>
              </div>
            </div>

            <form v-else @submit.prevent="handleSave" class="space-y-4">
              <BaseInput
                v-model="fullName"
                label="Nombre completo"
                required
                :error="errors.full_name"
              />
              <div class="flex gap-3">
                <BaseButton type="submit" :loading="saveLoading">Guardar</BaseButton>
                <BaseButton type="button" variant="secondary" @click="cancelEdit">Cancelar</BaseButton>
              </div>
            </form>
          </BaseCard>

          <ProfileReportHistory />

          <BaseCard>
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Historial de puntos</h2>
            <BaseSpinner v-if="txStore.loading && txStore.transactions.length === 0" size="sm" />
            <div v-else-if="txStore.transactions.length === 0" class="text-center py-8 text-gray-500">
              <IconStar class="w-10 h-10 mx-auto text-gray-300 mb-2" />
              <p>Aún no tienes movimientos de puntos</p>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="tx in txStore.transactions"
                :key="tx.id"
                class="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <BaseBadge :variant="txBadgeVariant(tx.type)" size="sm">
                    {{ txLabel(tx.type) }}
                  </BaseBadge>
                  <div class="min-w-0">
                    <p class="text-sm text-gray-900 truncate">{{ tx.description || txLabel(tx.type) }}</p>
                    <p class="text-xs text-gray-400">{{ formatDate(tx.created_at) }}</p>
                  </div>
                </div>
                <span
                  class="text-sm font-semibold shrink-0 ml-3"
                  :class="tx.type === 'earned' ? 'text-emerald-600' : 'text-red-500'"
                >
                  {{ tx.type === 'earned' ? '+' : '-' }}{{ tx.points }}
                </span>
              </div>
            </div>
          </BaseCard>
        </div>

        <div class="space-y-4">
          <BaseCard padding="md">
            <div class="text-center">
              <div class="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center mx-auto text-emerald-600 text-2xl font-bold">
                {{ (authStore.user?.full_name || '?').charAt(0).toUpperCase() }}
              </div>
              <h3 class="mt-3 font-semibold text-gray-900">{{ authStore.userName }}</h3>
            </div>
          </BaseCard>

          <BaseCard padding="md">
            <div class="text-center">
              <p class="text-sm text-gray-500">Puntos totales</p>
              <p class="text-3xl font-bold text-emerald-600 mt-1">{{ formatPoints(authStore.userPoints) }}</p>
            </div>
          </BaseCard>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
