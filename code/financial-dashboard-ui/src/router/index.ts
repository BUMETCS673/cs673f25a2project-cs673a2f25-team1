import { createRouter, createWebHistory } from 'vue-router'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/Dashboard.vue'),
    },
    {
      path: '/dashboard',
      name: 'dashboard-alt',
      component: () => import('../views/Dashboard.vue'),
    }
  ],
})

export default router
