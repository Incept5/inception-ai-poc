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
    <div class="message-content" :class="[message.type, { thinking: message.type === 'thinking' }]">
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

.bot .message-content.thinking {
  background-color: #f8f8f8;
  font-style: italic;
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

/* Add this new style for the blinking cursor */
.thinking::after {
  content: '';
  display: inline-block;
  width: 0.5em;
  height: 1em;
  margin-left: 0.2em;
  background-color: currentColor;
  animation: blink 0.7s infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>