<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/authStore'
import { useFormValidation } from '../composables/useFormValidation'
import { profileSchema } from '../utils/validators'
import { formatPoints } from '../utils/format'
import { api } from '../api/http'
import AppLayout from '../components/shared/AppLayout.vue'
import BaseCard from '../components/base/BaseCard.vue'
import BaseInput from '../components/base/BaseInput.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseAlert from '../components/base/BaseAlert.vue'

const authStore = useAuthStore()
const { errors, validate } = useFormValidation(profileSchema)

const editing = ref(false)
const fullName = ref(authStore.user?.full_name || '')
const saveLoading = ref(false)
const saveError = ref<string | null>(null)
const saveSuccess = ref(false)

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
  } catch (e: any) {
    saveError.value = e.message || 'Error al guardar'
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
</script>

<template>
  <AppLayout>
    <div class="max-w-2xl mx-auto space-y-6">
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
                <p class="text-gray-900 font-medium capitalize">{{ authStore.user?.role || '-' }}</p>
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
