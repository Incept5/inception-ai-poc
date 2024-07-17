<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { fetchBots, fetchModels, sendMessage } from '../api'
import ChatMessage from './ChatMessage.vue'
import TranscriptionListener from './TranscriptionListener.vue'

const props = defineProps(['initialThreadId'])
const emit = defineEmits(['thread-created', 'new-message-displayed'])

const bots = ref([])
const models = ref([])
const botSelector = ref('')
const llmSelector = ref('anthropic')
const modelSelector = ref('')
const userInput = ref('')
const messages = ref([])
const chatContainer = ref(null)
const threadId = ref(null)
const thinkingMessageIndex = ref(null)
const isWaitingForResponse = ref(false)

// Transcription-related refs
const isListening = ref(false)
const isConnecting = ref(false)
const isTranscriptionDisabled = ref(false)
const partialTranscription = ref('')
const lastPartialTranscriptionLength = ref(0)

const llmProviders = [
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Ollama', value: 'ollama' },
  { label: 'Groq', value: 'groq' }
]

// Computed property to determine if controls should be disabled
const areControlsDisabled = computed(() => isConnecting.value || isTranscriptionDisabled.value || isWaitingForResponse.value)

onMounted(async () => {
  await loadBots()
  await loadModels()
  initializeThread(props.initialThreadId)
})

watch(llmSelector, async () => {
  await loadModels()
  addSystemMessage(`LLM provider changed to ${llmSelector.value}`)
})

watch(botSelector, () => {
  addSystemMessage(`Bot changed to ${botSelector.value}`)
})

watch(modelSelector, () => {
  addSystemMessage(`Model changed to ${modelSelector.value}`)
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

function initializeThread(initialThreadId = null) {
  threadId.value = initialThreadId || Date.now().toString()
  messages.value = []
  addSystemMessage(`Conversation started. Thread ID: ${threadId.value}`)
  emit('thread-created', threadId.value)
}

function addSystemMessage(message) {
  messages.value.push({ sender: 'System', message: message })
  scrollToBottom()
}

async function handleSendMessage() {
  if (!userInput.value.trim() || areControlsDisabled.value) return

  // Stop listening if it's currently active
  if (isListening.value) {
    isListening.value = false
  }

  const userMessage = userInput.value
  messages.value.push({ sender: 'You', message: userMessage })
  userInput.value = '' // Clear the text area immediately after sending the message

  // Add thinking message
  thinkingMessageIndex.value = messages.value.length
  messages.value.push({ sender: 'Bot', message: 'Bot (thinking)...', type: 'thinking' })
  scrollToBottom()

  isWaitingForResponse.value = true

  try {
    // Ensure we're using the same threadId for all messages in the conversation
    if (!threadId.value) {
      initializeThread()
    }

    const responseStream = await sendMessage(
      botSelector.value,
      userMessage,
      llmSelector.value,
      modelSelector.value,
      threadId.value // Always send the current threadId
    )

    // Remove thinking message
    if (thinkingMessageIndex.value !== null) {
      messages.value.splice(thinkingMessageIndex.value, 1)
      thinkingMessageIndex.value = null
    }

    for await (const chunk of responseStream) {
      messages.value.push({
        sender: 'Bot',
        message: chunk.content,
        type: chunk.type
      })

      scrollToBottom()
    }

    // Emit the new-message-displayed event
    emit('new-message-displayed')
  } catch (error) {
    console.error('Error sending message:', error)
    // Remove thinking message in case of error
    if (thinkingMessageIndex.value !== null) {
      messages.value.splice(thinkingMessageIndex.value, 1)
      thinkingMessageIndex.value = null
    }
    addSystemMessage('Failed to send message. Please try again.')
  } finally {
    isWaitingForResponse.value = false
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

// Transcription-related functions
function toggleListening() {
  if (!isConnecting.value && !isTranscriptionDisabled.value) {
    isListening.value = !isListening.value
    if (!isListening.value) {
      // Reset partial transcription when stopping listening
      partialTranscription.value = ''
      lastPartialTranscriptionLength.value = 0
    }
  }
}

function handlePartialTranscription(message) {
  // Remove the previous partial transcription
  if (lastPartialTranscriptionLength.value > 0) {
    userInput.value = userInput.value.slice(0, -lastPartialTranscriptionLength.value)
  }

  // Update the partial transcription and its length
  partialTranscription.value = message.text
  lastPartialTranscriptionLength.value = partialTranscription.value.length

  // Append the new partial transcription
  userInput.value += partialTranscription.value
}

function handleFinalTranscription(message) {
  // Remove the last partial transcription
  if (lastPartialTranscriptionLength.value > 0) {
    userInput.value = userInput.value.slice(0, -lastPartialTranscriptionLength.value)
  }

  // Append the final transcription to the existing userInput
  userInput.value += ' ' + message.text

  // Reset partial transcription and its length
  partialTranscription.value = ''
  lastPartialTranscriptionLength.value = 0
}

function handleTranscriptionError(errorMessage) {
  console.error('Transcription error:', errorMessage)
  isListening.value = false
  isConnecting.value = false
  if (errorMessage.includes('ASSEMBLYAI_API_KEY not set') || errorMessage.includes('AssemblyAI configuration')) {
    isTranscriptionDisabled.value = true
  }
}

function handleTranscriptionStatusChange(status) {
  isConnecting.value = status === 'connecting'
  isTranscriptionDisabled.value = status === 'disabled'
  if (status === 'disabled') {
    isListening.value = false
  }
}

function handleKeyDown(event) {
  if (event.key === 'Enter' && !event.shiftKey && !areControlsDisabled.value) {
    event.preventDefault()
    handleSendMessage()
  }
}
</script>

<template>
  <div class="chatbot-container">
    <div class="controls">
      <div class="top-row">
        <div class="bot-selector-wrapper">
          <select v-model="botSelector" :disabled="areControlsDisabled">
            <option v-for="bot in bots" :key="bot.bot_type" :value="bot.bot_type">
              {{ bot.description }}
            </option>
          </select>
        </div>
        <button @click="initializeThread()" class="new-conversation-btn" :disabled="areControlsDisabled">New Conversation</button>
      </div>
      <div class="bottom-row">
        <select v-model="llmSelector" :disabled="areControlsDisabled">
          <option v-for="provider in llmProviders" :key="provider.value" :value="provider.value">
            {{ provider.label }}
          </option>
        </select>
        <select v-model="modelSelector" :disabled="areControlsDisabled">
          <option v-for="model in models" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
      </div>
    </div>
    <div ref="chatContainer" class="chat-messages">
      <ChatMessage v-for="(message, index) in messages" :key="index" :message="message" />
    </div>
    <div class="input-area">
      <textarea
        v-model="userInput"
        @keydown="handleKeyDown"
        placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
        rows="3"
        :disabled="areControlsDisabled"
      ></textarea>
    </div>
    <div class="transcription-and-send-controls">
      <div class="transcription-controls">
        <button @click="toggleListening" :class="['toggle-button', { 'active': isListening, 'disabled': areControlsDisabled }]" :disabled="areControlsDisabled">
          {{ isListening ? 'Stop Listening' : isConnecting ? 'Connecting...' : isTranscriptionDisabled ? 'Transcription Unavailable' : 'Start Listening' }}
        </button>
        <div class="transcription-status">
          <span :class="['status-indicator', { 'active': isListening, 'connecting': isConnecting, 'disabled': isTranscriptionDisabled }]"></span>
          {{ isListening ? 'Listening...' : isConnecting ? 'Connecting...' : isTranscriptionDisabled ? 'Transcription Disabled' : 'Not Listening' }}
        </div>
      </div>
      <button @click="handleSendMessage" class="send-button" :disabled="areControlsDisabled">Go</button>
    </div>
    <TranscriptionListener
      :enabled="isListening"
      @partial-transcription-received="handlePartialTranscription"
      @final-transcription-received="handleFinalTranscription"
      @error="handleTranscriptionError"
      @status-change="handleTranscriptionStatusChange"
    />
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
  max-height: calc(100vh - 360px);
}

.input-area {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

textarea {
  width: 100%;
  padding: 5px;
  resize: vertical;
  min-height: 60px;
}

.transcription-and-send-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.transcription-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.transcription-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 10px;
  background-color: #ccc;
}

.status-indicator.active {
  background-color: #4CAF50;
}

.status-indicator.connecting {
  background-color: #FFA500;
}

.status-indicator.disabled {
  background-color: #FF0000;
}

/* Add this new style for the blinking cursor */
.chat-messages :deep(.thinking::after) {
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

/* Add styles for disabled controls */
select:disabled,
button:disabled,
textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>