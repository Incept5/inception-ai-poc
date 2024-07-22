<script setup>
import { RouterView } from 'vue-router'
import HamburgerMenu from './components/HamburgerMenu.vue'
</script>

<template>
  <div class="app-container">
    <header>
      <h1>Inception AI Chatbot</h1>
      <HamburgerMenu />
    </header>
    <main>
      <RouterView v-slot="{ Component }">
        <template v-if="Component">
          <component :is="Component" />
        </template>
        <template v-else>
          <p>No component loaded</p>
        </template>
      </RouterView>
    </main>
  </div>
</template>

<style>
/* Reset default margins and paddings */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

body {
  font-family: Arial, sans-serif;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

header {
  background-color: #4a90e2;
  color: white;
  padding: 1rem;
  text-align: center;
  position: relative;
}

main {
  flex: 1;
  overflow: hidden;
}
</style>