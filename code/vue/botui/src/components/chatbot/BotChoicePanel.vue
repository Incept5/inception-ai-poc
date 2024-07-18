<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { fetchBots, fetchLLMProviders } from '../../api'

const props = defineProps(['initialThreadId'])
const emit = defineEmits(['bot-changed', 'llm-changed', 'model-changed', 'new-conversation'])

const bots = ref([])
const llmProviders = ref([])
const botSelector = ref('')
const llmSelector = ref('')
const modelSelector = ref('')

const lastBotEmitted = ref('')
const lastLlmEmitted = ref('')
const lastModelEmitted = ref('')

const areControlsDisabled = computed(() => props.isDisabled)

watch(llmSelector, () => {
  updateModelOptions()
  emitLlmChanged()
})

watch(botSelector, () => {
  emitBotChanged()
  updateLlmSettings()
})

watch(modelSelector, () => {
  emitModelChanged()
})

function emitBotChanged() {
  if (botSelector.value !== lastBotEmitted.value) {
    lastBotEmitted.value = botSelector.value
    emit('bot-changed', botSelector.value)
  }
}

function emitLlmChanged() {
  if (llmSelector.value !== lastLlmEmitted.value) {
    lastLlmEmitted.value = llmSelector.value
    emit('llm-changed', llmSelector.value)
  }
}

function emitModelChanged() {
  if (modelSelector.value !== lastModelEmitted.value) {
    lastModelEmitted.value = modelSelector.value
    emit('model-changed', modelSelector.value)
  }
}

async function loadBots() {
  try {
    bots.value = await fetchBots()
    if (bots.value.length > 0) {
      botSelector.value = bots.value[0].bot_type
      updateLlmSettings()
    }
  } catch (error) {
    console.error('Error loading bots:', error)
  }
}

async function loadLLMProviders() {
  try {
    llmProviders.value = await fetchLLMProviders()
  } catch (error) {
    console.error('Error loading LLM providers:', error)
  }
}

function updateModelOptions() {
  const selectedProvider = llmProviders.value.find(p => p.provider === llmSelector.value)
  if (selectedProvider && selectedProvider.models.length > 0) {
    modelSelector.value = selectedProvider.models[0]
    emitModelChanged()
  }
}

function updateLlmSettings() {
  const selectedBot = bots.value.find(bot => bot.bot_type === botSelector.value)
  if (selectedBot) {
    const botDefaultProvider = selectedBot.config_options.llm_provider.default
    const botDefaultModel = selectedBot.config_options.llm_model.default

    if (botDefaultProvider && botDefaultProvider !== 'None' && llmProviders.value.some(p => p.provider === botDefaultProvider)) {
      llmSelector.value = botDefaultProvider
    } else if (llmProviders.value.length > 0) {
      llmSelector.value = llmProviders.value[0].provider
    }

    const selectedProvider = llmProviders.value.find(p => p.provider === llmSelector.value)
    if (selectedProvider) {
      if (botDefaultModel && botDefaultModel !== 'None' && selectedProvider.models.includes(botDefaultModel)) {
        modelSelector.value = botDefaultModel
      } else if (selectedProvider.models.length > 0) {
        modelSelector.value = selectedProvider.models[0]
      }
    }

    emitLlmChanged()
    emitModelChanged()
  }
}

function handleNewConversation() {
  emit('new-conversation')
}

onMounted(async () => {
  await loadLLMProviders()
  await loadBots()
})
</script>

<template>
  <div class="controls">
    <div class="top-row">
      <div class="bot-selector-wrapper">
        <select v-model="botSelector" :disabled="areControlsDisabled">
          <option v-for="bot in bots" :key="bot.bot_type" :value="bot.bot_type">
            {{ bot.description }}
          </option>
        </select>
      </div>
      <button @click="handleNewConversation" class="new-conversation-btn" :disabled="areControlsDisabled">New Conversation</button>
    </div>
    <div class="bottom-row">
      <select v-model="llmSelector" :disabled="areControlsDisabled">
        <option v-for="provider in llmProviders" :key="provider.provider" :value="provider.provider">
          {{ provider.provider }}
        </option>
      </select>
      <select v-model="modelSelector" :disabled="areControlsDisabled">
        <option v-for="model in llmProviders.find(p => p.provider === llmSelector)?.models || []" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
    </div>
  </div>
</template>