<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { sendMessage } from '../../api'
import ChatMessage from './ChatMessage.vue'
import TranscriptionListener from './TranscriptionListener.vue'
import BotChoicePanel from './BotChoicePanel.vue'
import './css/ChatBot.css'

const props = defineProps(['initialThreadId'])
const emit = defineEmits(['thread-created', 'new-message-displayed', 'loading-change', 'output-url-detected'])

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

// Add these new refs to store the selected values from BotChoicePanel
const selectedBot = ref('')
const selectedLlm = ref('')
const selectedModel = ref('')

let loadingTimeout = null

// Computed property to determine if controls should be disabled
const areControlsDisabled = computed(() => isConnecting.value || isTranscriptionDisabled.value || isWaitingForResponse.value)

onMounted(() => {
  initializeThread(props.initialThreadId)
})

const setLoading = (value) => {
  clearTimeout(loadingTimeout);
  if (value) {
    isWaitingForResponse.value = true;
    emit('loading-change', true);
  } else {
    loadingTimeout = setTimeout(() => {
      isWaitingForResponse.value = false;
      emit('loading-change', false);
    }, 200);
  }
};

function processPublishedFiles(message) {
  console.log('Processing message for published files:', message)
  const regex = /(\S+:\/mnt\/__threads\/\d+\/[^\s)]+)/g
  let match;
  let processedMessage = message;

  while ((match = regex.exec(message)) !== null) {
    console.log('Published file path detected:', match[1])
    const sandboxPath = match[1]
    const publishedUrl = sandboxPath.replace(/^\S+:\/mnt/, '/published')
    console.log('Emitting output-url-detected event with URL:', publishedUrl)
    emit('output-url-detected', publishedUrl)
    processedMessage = processedMessage.replace(sandboxPath, publishedUrl)
  }

  console.log('Processed message:', processedMessage)
  return processedMessage
}

async function handleSendMessage() {
  if (!userInput.value.trim() || areControlsDisabled.value) return

  if (isListening.value) {
    isListening.value = false
  }

  const userMessage = userInput.value
  messages.value.push({ sender: 'You', message: userMessage })
  userInput.value = ''

  thinkingMessageIndex.value = messages.value.length
  messages.value.push({ sender: 'Bot', message: 'Bot (thinking)...', type: 'thinking' })
  scrollToBottom()

  setLoading(true)

  try {
    if (!threadId.value) {
      initializeThread()
    }

    const responseStream = await sendMessage(
      selectedBot.value,
      userMessage,
      selectedLlm.value,
      selectedModel.value,
      threadId.value
    )

    if (thinkingMessageIndex.value !== null) {
      messages.value.splice(thinkingMessageIndex.value, 1)
      thinkingMessageIndex.value = null
    }

    for await (const chunk of responseStream) {
      console.log('Received chunk:', chunk)
      const processedMessage = processPublishedFiles(chunk.content)
      messages.value.push({
        sender: 'Bot',
        message: processedMessage,
        type: chunk.type
      })

      scrollToBottom()
    }

    console.log('Final messages array:', messages.value)
    emit('new-message-displayed')
  } catch (error) {
    console.error('Error sending message:', error)
    if (thinkingMessageIndex.value !== null) {
      messages.value.splice(thinkingMessageIndex.value, 1)
      thinkingMessageIndex.value = null
    }
    addSystemMessage('Failed to send message. Please try again.')
  } finally {
    setLoading(false)
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

// Transcription-related functions
function toggleListening() {
  if (!isConnecting.value && !isTranscriptionDisabled.value) {
    isListening.value = !isListening.value
    if (!isListening.value) {
      partialTranscription.value = ''
      lastPartialTranscriptionLength.value = 0
    }
  }
}

function handlePartialTranscription(message) {
  if (lastPartialTranscriptionLength.value > 0) {
    userInput.value = userInput.value.slice(0, -lastPartialTranscriptionLength.value)
  }

  partialTranscription.value = message.text
  lastPartialTranscriptionLength.value = partialTranscription.value.length

  userInput.value += partialTranscription.value
}

function handleFinalTranscription(message) {
  if (lastPartialTranscriptionLength.value > 0) {
    userInput.value = userInput.value.slice(0, -lastPartialTranscriptionLength.value)
  }

  userInput.value += ' ' + message.text

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

function handleBotChanged(bot) {
  selectedBot.value = bot
  addSystemMessage(`Bot changed to ${bot}`)
}

function handleLlmChanged(llm) {
  selectedLlm.value = llm
  addSystemMessage(`LLM provider changed to ${llm}`)
}

function handleModelChanged(model) {
  selectedModel.value = model
  addSystemMessage(`Model changed to ${model}`)
}

function handleNewConversation() {
  initializeThread()
}
</script>

<template>
  <div class="chatbot-container">
    <BotChoicePanel
      :initial-thread-id="initialThreadId"
      :is-disabled="areControlsDisabled"
      @bot-changed="handleBotChanged"
      @llm-changed="handleLlmChanged"
      @model-changed="handleModelChanged"
      @new-conversation="handleNewConversation"
    />
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