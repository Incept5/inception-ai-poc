import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory('/botui/'), // Update this line to use '/botui/' as the base
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/thread/:threadId?',
      name: 'thread',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router