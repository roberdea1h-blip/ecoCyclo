<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useFormValidation } from '../composables/useFormValidation'
import { registerSchema } from '../utils/validators'
import BaseInput from '../components/base/BaseInput.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseAlert from '../components/base/BaseAlert.vue'

const router = useRouter()
const authStore = useAuthStore()
const { errors, validate } = useFormValidation(registerSchema)

const form = reactive({
  email: '',
  password: '',
  full_name: '',
})

async function handleSubmit() {
  if (!validate(form)) return
  try {
    await authStore.register(form.email, form.password, form.full_name)
    router.push('/dashboard')
  } catch {
    // error handled by store
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-emerald-600">EcoCycle</h1>
        <p class="mt-2 text-gray-600">Crea tu cuenta</p>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sm:p-8">
        <BaseAlert v-if="authStore.error" variant="error" class="mb-4">
          {{ authStore.error }}
        </BaseAlert>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <BaseInput
            v-model="form.full_name"
            label="Nombre completo"
            placeholder="Tu nombre"
            required
            :error="errors.full_name"
          />
          <BaseInput
            v-model="form.email"
            label="Correo electrónico"
            type="email"
            placeholder="tucorreo@ejemplo.com"
            required
            :error="errors.email"
          />
          <BaseInput
            v-model="form.password"
            label="Contraseña"
            type="password"
            placeholder="Mínimo 6 caracteres"
            required
            :error="errors.password"
          />
          <BaseButton type="submit" :loading="authStore.loading" class="w-full">
            Crear cuenta
          </BaseButton>
        </form>
        <p class="mt-4 text-center text-sm text-gray-600">
          ¿Ya tienes cuenta?
          <router-link to="/login" class="text-emerald-600 hover:text-emerald-700 font-medium">
            Inicia sesión
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>
