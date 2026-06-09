import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('../views/ReportsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reports/create',
      name: 'ReportCreate',
      component: () => import('../views/ReportCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reports/:id',
      name: 'ReportDetail',
      component: () => import('../views/ReportDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/rewards',
      name: 'Rewards',
      component: () => import('../views/RewardsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/notifications',
      name: 'Notifications',
      component: () => import('../views/NotificationsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, role: 'admin' },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login' })
    return
  }

  if (to.meta.guest && token) {
    next({ name: 'Dashboard' })
    return
  }

  if (to.meta.role === 'admin') {
    // Defer to the store check: we import async to avoid circular deps
    import('../stores/authStore').then(({ useAuthStore }) => {
      const authStore = useAuthStore()
      if (!authStore.isAdmin) {
        next({ name: 'Dashboard' })
      } else {
        next()
      }
    })
    return
  }

  next()
})

export default router
