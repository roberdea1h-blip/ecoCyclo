<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import { useNotificationPolling } from '../../composables/useNotificationPolling'
import IconLogout from '../icons/IconLogout.vue'
import IconUser from '../icons/IconUser.vue'

const router = useRouter()
const route = useRoute()
const { isAuthenticated, isAdmin, userName, logout } = useAuth()
const { unreadCount } = useNotificationPolling()

const mobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Reportes', path: '/reports' },
  { name: 'Recompensas', path: '/rewards' },
  { name: 'Notificaciones', path: '/notifications' },
]

async function handleLogout() {
  await logout()
  router.push('/login')
}

function isActive(path: string) {
  if (path === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(path)
}
</script>

<template>
  <nav v-if="isAuthenticated" class="bg-white border-b border-gray-200 sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-8">
          <router-link to="/dashboard" class="flex items-center gap-2">
            <span class="text-xl font-bold text-emerald-600">EcoCycle</span>
          </router-link>
          <div class="hidden md:flex items-center gap-1">
            <router-link
              v-for="link in navLinks"
              :key="link.path"
              :to="link.path"
              class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="isActive(link.path) ? 'bg-emerald-50 text-emerald-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
            >
              {{ link.name }}
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/admin"
              class="px-3 py-2 rounded-lg text-sm font-medium transition-colors"
              :class="isActive('/admin') ? 'bg-emerald-50 text-emerald-700' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
            >
              Admin
            </router-link>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <router-link to="/notifications" class="relative p-2 text-gray-500 hover:text-gray-700 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span
              v-if="unreadCount > 0"
              class="absolute -top-0.5 -right-0.5 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full"
            >
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </router-link>
          <router-link
            to="/profile"
            class="hidden md:flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
          >
            <div class="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 font-semibold text-xs">
              {{ userName.charAt(0).toUpperCase() }}
            </div>
            <span class="max-w-[120px] truncate">{{ userName }}</span>
          </router-link>
          <button
            class="hidden md:inline-flex text-sm text-gray-500 hover:text-red-600 transition-colors items-center gap-2  "
            @click="handleLogout"
          >
            <IconLogout />
            Salir
          </button>
          <button class="md:hidden p-2 text-gray-500" @click="mobileMenuOpen = !mobileMenuOpen">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="mobileMenuOpen" class="md:hidden pb-3 border-t border-gray-100 pt-2">
          <router-link
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="block px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive(link.path) ? 'bg-emerald-50 text-emerald-700' : 'text-gray-600 hover:bg-gray-50'"
            @click="mobileMenuOpen = false"
          >
            {{ link.name }}
          </router-link>
          <router-link
            v-if="isAdmin"
            to="/admin"
            class="block px-3 py-2 rounded-lg text-sm font-medium transition-colors"
            :class="isActive('/admin') ? 'bg-emerald-50 text-emerald-700' : 'text-gray-600 hover:bg-gray-50'"
            @click="mobileMenuOpen = false"
          >
            Admin
          </router-link>
          <router-link
            to="/profile"
            class="block px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50"
            @click="mobileMenuOpen = false"
          >
            <div class="flex items-center gap-2">
              Perfil
              <IconUser class=" size-5 "/>
            </div>
          </router-link>
          <button
            class="flex gap-2 items-center w-full text-left px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50"
            @click="handleLogout"
          >
            Cerrar sesión
            <IconLogout/>
          </button>
        </div>
      </Transition>
    </div>
  </nav>
</template>
