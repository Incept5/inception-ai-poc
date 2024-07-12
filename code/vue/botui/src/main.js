import './assets/main.css'
import './assets/global.css'  // Add this line

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import 'highlight.js/styles/default.css'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'

hljs.registerLanguage('javascript', javascript)

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

// Initialize highlight.js
app.directive('highlight', {
  mounted(el) {
    hljs.highlightElement(el)
  }
})