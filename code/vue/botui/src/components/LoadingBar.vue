<template>
  <div class="loading-bar-container">
    <div class="loading-bar" :style="{ width: `${progress}%` }"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
});

const progress = ref(0);
let animationFrame;
const fillDuration = 2000; // 2 seconds for filling
const drainDuration = 2000; // 2 seconds for draining
const startTime = ref(0);
const isFilling = ref(true);

const animate = (timestamp) => {
  if (!startTime.value) startTime.value = timestamp;
  const elapsedTime = timestamp - startTime.value;

  if (isFilling.value) {
    progress.value = Math.min((elapsedTime / fillDuration) * 100, 100);
    if (progress.value === 100) {
      isFilling.value = false;
      startTime.value = timestamp;
    }
  } else {
    progress.value = Math.max(100 - (elapsedTime / drainDuration) * 100, 0);
    if (progress.value === 0) {
      isFilling.value = true;
      startTime.value = timestamp;
    }
  }

  if (props.isLoading) {
    animationFrame = requestAnimationFrame(animate);
  } else {
    progress.value = 0;
  }
};

const startLoading = () => {
  cancelAnimationFrame(animationFrame);
  startTime.value = 0;
  progress.value = 0;
  isFilling.value = true;
  animationFrame = requestAnimationFrame(animate);
};

watch(() => props.isLoading, (newValue) => {
  if (newValue) {
    startLoading();
  } else {
    cancelAnimationFrame(animationFrame);
    progress.value = 0;
  }
});

onMounted(() => {
  if (props.isLoading) {
    startLoading();
  }
});

onUnmounted(() => {
  cancelAnimationFrame(animationFrame);
});
</script>

<style scoped>
.loading-bar-container {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: white;
  overflow: hidden;
  z-index: 9999;
}

.loading-bar {
  height: 100%;
  background-color: #4285f4;
  transition: width 0.1s linear;
}
</style>