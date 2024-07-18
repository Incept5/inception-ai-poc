<script setup>
import { ref, watch } from 'vue'

const props = defineProps(['url'])
const imageUrl = ref('')

watch(() => props.url, (newUrl) => {
  if (newUrl) {
    imageUrl.value = newUrl
  }
}, { immediate: true })
</script>

<template>
  <div class="output-tab">
    <img v-if="imageUrl" :src="imageUrl" alt="Output" class="output-image" />
    <p v-else>No output to display</p>
  </div>
</template>

<style scoped>
.output-tab {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.output-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
</style>