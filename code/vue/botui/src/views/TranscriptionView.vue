<template>
  <div class="transcription-view">
    <header>
      <h1 class="header__title">Real-Time Transcription</h1>
      <p class="header__sub-title">
        Try AssemblyAI's new real-time transcription endpoint!
      </p>
    </header>
    <div class="transcription-container">
      <div class="transcription-status">
        <span :class="['status-indicator', { 'active': isListening, 'connecting': isConnecting, 'disabled': isDisabled }]"></span>
        {{ statusText }}
      </div>
      <div class="transcription-text">
        <p>{{ displayedTranscription }}</p>
      </div>
      <button @click="toggleListening" :class="['toggle-button', { 'active': isListening, 'disabled': isConnecting || isDisabled }]" :disabled="isConnecting || isDisabled">
        {{ buttonText }}
      </button>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
    <TranscriptionListener
      :enabled="isListening"
      @partial-transcription-received="handlePartialTranscription"
      @final-transcription-received="handleFinalTranscription"
      @error="handleError"
      @status-change="handleStatusChange"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import TranscriptionListener from '../components/TranscriptionListener.vue';

export default {
  name: 'TranscriptionView',
  components: {
    TranscriptionListener,
  },
  setup() {
    const completedTranscription = ref('');
    const partialTranscription = ref('');
    const isListening = ref(false);
    const isConnecting = ref(false);
    const isDisabled = ref(false);
    const error = ref('');

    const displayedTranscription = computed(() => {
      return completedTranscription.value + (partialTranscription.value ? ' ' + partialTranscription.value : '');
    });

    const statusText = computed(() => {
      if (isDisabled.value) return 'Transcription Disabled';
      if (isConnecting.value) return 'Connecting...';
      if (isListening.value) return 'Listening...';
      return 'Not Listening';
    });

    const buttonText = computed(() => {
      if (isDisabled.value) return 'Transcription Unavailable';
      if (isConnecting.value) return 'Connecting...';
      return isListening.value ? 'Stop Listening' : 'Start Listening';
    });

    const handlePartialTranscription = (message) => {
      console.log('Partial transcription:', message);
      partialTranscription.value = message.text;
    };

    const handleFinalTranscription = (message) => {
      console.log('Final transcription:', message);
      completedTranscription.value += (completedTranscription.value ? ' ' : '') + message.text;
      partialTranscription.value = ''; // Reset partial transcription
    };

    const toggleListening = () => {
      if (!isConnecting.value && !isDisabled.value) {
        isListening.value = !isListening.value;
        if (!isListening.value) {
          error.value = ''; // Clear any previous errors when stopping
        }
      }
    };

    const handleError = (errorMessage) => {
      console.error('Transcription error:', errorMessage);
      error.value = errorMessage;
      isListening.value = false;
      isConnecting.value = false;
      if (errorMessage.includes('ASSEMBLYAI_API_KEY not set') || errorMessage.includes('AssemblyAI configuration')) {
        isDisabled.value = true;
      }
    };

    const handleStatusChange = (status) => {
      isConnecting.value = status === 'connecting';
      isDisabled.value = status === 'disabled';
      if (status === 'disabled') {
        isListening.value = false;
      }
    };

    return {
      displayedTranscription,
      isListening,
      isConnecting,
      isDisabled,
      error,
      statusText,
      buttonText,
      handlePartialTranscription,
      handleFinalTranscription,
      toggleListening,
      handleError,
      handleStatusChange,
    };
  },
};
</script>

<style scoped>
.transcription-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header__title {
  font-size: 2em;
  margin-bottom: 10px;
}

.header__sub-title {
  font-size: 1.2em;
  margin-bottom: 20px;
}

.transcription-container {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.transcription-status {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
  margin-right: 10px;
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

.transcription-text {
  min-height: 100px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin-bottom: 10px;
}

.toggle-button {
  padding: 10px 20px;
  font-size: 1em;
  cursor: pointer;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.toggle-button:hover {
  background-color: #45a049;
}

.toggle-button.active {
  background-color: #f44336;
}

.toggle-button.active:hover {
  background-color: #d32f2f;
}

.toggle-button.disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #f44336;
  margin-top: 10px;
  font-weight: bold;
}
</style>