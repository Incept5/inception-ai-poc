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
    const responseStream = await sendMessage(
      botSelector.value,
      userMessage,
      llmSelector.value,
      modelSelector.value,
      threadId.value
    )

    let currentResponse = { sender: 'Bot', message: '', type: 'intermediate' }

    for await (const chunk of responseStream) {
      if (chunk.type === 'intermediate') {
        currentResponse.message += chunk.content
        currentResponse.type = 'intermediate'
      } else if (chunk.type === 'final') {
        currentResponse.message += chunk.content
        currentResponse.type = 'final'
      }

      // Update or add the message to the conversation
      const existingMessageIndex = messages.value.findIndex(m => m.sender === 'Bot' && m.type === 'intermediate')
      if (existingMessageIndex !== -1) {
        messages.value[existingMessageIndex] = { ...currentResponse }
      } else {
        messages.value.push({ ...currentResponse })
      }

      // Scroll to the bottom of the chat container
      scrollToBottom()
    }

    // If the last message is still intermediate, change it to final
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage.sender === 'Bot' && lastMessage.type === 'intermediate') {
      lastMessage.type = 'final'
    }

  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({ sender: 'Error', message: 'Failed to send message. Please try again.' })
  }

  scrollToBottom()
}

function scrollToBottom() {
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
      <div class="top-row">
        <div class="bot-selector-wrapper">
          <select v-model="botSelector">
            <option v-for="bot in bots" :key="bot.bot_type" :value="bot.bot_type">
              {{ bot.description }}
            </option>
          </select>
        </div>
        <button @click="initializeThread" class="new-conversation-btn">New Conversation</button>
      </div>
      <div class="bottom-row">
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
      </div>
    </div>
    <div ref="chatContainer" class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="[message.sender.toLowerCase(), message.type]">
        <strong>{{ message.sender === 'Bot' && message.type === 'intermediate' ? 'Bot (thinking):' : message.sender }}:</strong> {{ message.message }}
      </div>
    </div>
    <div class="input-area">
      <input v-model="userInput" @keyup.enter="handleSendMessage" placeholder="Type your message here...">
      <button @click="handleSendMessage">Send</button>
    </div>
  </div>
</template>

<style scoped>
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 20px;
}

.controls {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.top-row, .bottom-row {
  display: flex;
  gap: 10px;
}

.top-row {
  justify-content: space-between;
  align-items: center;
}

.bottom-row {
  justify-content: flex-start;
}

.bot-selector-wrapper {
  flex: 1;
  min-width: 0;
}

select, button {
  padding: 5px 10px;
  font-size: 14px;
}

select {
  width: 100%;
}

.new-conversation-btn {
  white-space: nowrap;
  flex-shrink: 0;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
  max-height: calc(100vh - 220px);
}

.message {
  margin-bottom: 10px;
}

.you {
  text-align: right;
}

.bot {
  text-align: left;
}

.intermediate {
  opacity: 0.7;
}

.input-area {
  display: flex;
  gap: 10px;
  padding-bottom: 10px;
}

input {
  flex-grow: 1;
  padding: 5px;
}

button {
  padding: 5px 10px;
}
</style>