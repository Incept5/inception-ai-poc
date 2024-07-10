<script setup>
import { ref, onMounted, watch } from 'vue'
import { fetchBots, fetchModels, sendMessage } from '../api'

const bots = ref([])
const models = ref([])
const botSelector = ref('')
const llmSelector = ref('anthropic')
const modelSelector = ref('')
const userInput = ref('')
const messages = ref([])
const showThinking = ref(false)
const chatContainer = ref(null)
const threadId = ref(null)

const llmProviders = [
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Ollama', value: 'ollama' },
  { label: 'Groq', value: 'groq' }
]

onMounted(async () => {
  await loadBots()
  await loadModels()
})

watch(llmSelector, async () => {
  await loadModels()
})

async function loadBots() {
  try {
    bots.value = await fetchBots()
    if (bots.value.length > 0) {
      botSelector.value = bots.value[0].bot_type
    }
  } catch (error) {
    console.error('Error loading bots:', error)
  }
}

async function loadModels() {
  try {
    models.value = await fetchModels(llmSelector.value)
    if (models.value.length > 0) {
      modelSelector.value = models.value[0]
    }
  } catch (error) {
    console.error('Error loading models:', error)
  }
}

function initializeThread() {
  threadId.value = Date.now().toString()
  messages.value = []
}

async function handleSendMessage() {
  if (!userInput.value.trim()) return

  const userMessage = userInput.value
  messages.value.push({ sender: 'You', message: userMessage })
  userInput.value = ''

  try {
    const response = await sendMessage(
      botSelector.value,
      userMessage,
      llmSelector.value,
      modelSelector.value,
      threadId.value
    )

    // Handle the response stream
    const reader = response.getReader()
    let botResponse = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = new TextDecoder().decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonData = line.slice(5).trim()
          if (jsonData === '[DONE]') {
            break
          }

          try {
            const parsedData = JSON.parse(jsonData)
            if (parsedData.type === 'content') {
              botResponse += parsedData.content
            } else if (parsedData.type === 'thinking' && showThinking.value) {
              messages.value.push({ sender: 'Bot (thinking)', message: parsedData.content })
            }
          } catch (error) {
            console.error('Error parsing JSON:', error)
          }
        }
      }
    }

    if (botResponse) {
      messages.value.push({ sender: 'Bot', message: botResponse })
    }
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({ sender: 'Error', message: 'Failed to send message. Please try again.' })
  }

  // Scroll to the bottom of the chat container
  setTimeout(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  }, 0)
}
</script>

<template>
  <div class="chatbot-container">
    <div class="controls">
      <select v-model="botSelector">
        <option v-for="bot in bots" :key="bot.bot_type" :value="bot.bot_type">
          {{ bot.description }}
        </option>
      </select>
      <select v-model="llmSelector">
        <option v-for="provider in llmProviders" :key="provider.value" :value="provider.value">
          {{ provider.label }}
        </option>
      </select>
      <select v-model="modelSelector">
        <option v-for="model in models" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
      <label>
        <input type="checkbox" v-model="showThinking"> Show Thinking
      </label>
      <button @click="initializeThread">New Conversation</button>
    </div>
    <div ref="chatContainer" class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.sender.toLowerCase()">
        <strong>{{ message.sender }}:</strong> {{ message.message }}
      </div>
    </div>
    <div class="input-area">
      <input v-model="userInput" @keyup.enter="handleSendMessage" placeholder="Type your message here...">
      <button @click="handleSendMessage">Send</button>
    </div>
  </div>
</template>

<style scoped>
/* Keep the existing styles unchanged */
</style>