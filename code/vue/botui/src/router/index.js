import { createRouter, createWebHistory } from 'vue-router'
import ChatBotView from '../views/ChatBotView.vue'

const router = createRouter({
  history: createWebHistory('/botui/'),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ChatBotView
    },
    {
      path: '/thread/:threadId?',
      name: 'thread',
      component: ChatBotView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router