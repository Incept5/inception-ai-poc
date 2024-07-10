<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <div class="message" :class="message.sender.toLowerCase()">
    <div class="message-content" :class="message.type">
      <span class="message-label">{{ message.label || message.sender }}:</span>
      <span class="message-text">{{ message.message }}</span>
    </div>
  </div>
</template>

<style scoped>
.message {
  margin-bottom: 15px;
}

.message-content {
  display: inline-block;
  padding: 10px;
  border-radius: 10px;
  max-width: 100%;
  word-wrap: break-word;
}

.you .message-content {
  background-color: #e6f3ff;
}

.bot .message-content {
  background-color: #f0f0f0;
}

.system .message-content {
  background-color: #ffe6e6;
  font-style: italic;
}

.bot .message-content.intermediate {
  background-color: #e0e0e0;
}

.bot .message-content.final {
  background-color: #e6ffe6;
}

.message-label {
  font-weight: bold;
  margin-right: 5px;
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
}
</style>