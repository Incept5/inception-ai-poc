<template>
  <div class="hamburger-menu">
    <button @click="toggleMenu" class="hamburger-button">
      <span></span>
      <span></span>
      <span></span>
    </button>
    <nav v-show="isOpen" class="menu-items">
      <router-link to="/" @click="closeMenu">Home</router-link>
      <router-link to="/about" @click="closeMenu">About</router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const isOpen = ref(false);

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const closeMenu = () => {
  isOpen.value = false;
};
</script>

<style scoped>
.hamburger-menu {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
}

.hamburger-button {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  width: 2rem;
  height: 2rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}

.hamburger-button span {
  width: 2rem;
  height: 0.25rem;
  background: white;
  border-radius: 10px;
  transition: all 0.3s linear;
  position: relative;
  transform-origin: 1px;
}

.menu-items {
  position: absolute;
  top: 3rem;
  right: 0;
  background: white;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.menu-items a {
  color: #4a90e2;
  text-decoration: none;
  padding: 0.5rem 1rem;
  transition: background-color 0.3s;
}

.menu-items a:hover {
  background-color: #f0f0f0;
}
</style>