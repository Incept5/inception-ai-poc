import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TranscriptionView from '../views/TranscriptionView.vue'

const router = createRouter({
  history: createWebHistory('/botui/'),
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
    },
    {
      path: '/transcribe',
      name: 'transcribe',
      component: TranscriptionView
    }
  ]
})

export default router