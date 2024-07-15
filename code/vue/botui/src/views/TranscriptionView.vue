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
        <span :class="['status-indicator', { 'active': isListening }]"></span>
        {{ isListening ? 'Listening...' : 'Initializing...' }}
      </div>
      <div class="transcription-text">
        <p>{{ displayedTranscription }}</p>
      </div>
    </div>
    <TranscriptionListener
      @partial-transcription-received="handlePartialTranscription"
      @final-transcription-received="handleFinalTranscription"
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

    const displayedTranscription = computed(() => {
      return completedTranscription.value + (partialTranscription.value ? ' ' + partialTranscription.value : '');
    });

    const handlePartialTranscription = (message) => {
      console.log('Partial transcription:', message);
      partialTranscription.value = message.text;
      isListening.value = true;
    };

    const handleFinalTranscription = (message) => {
      console.log('Final transcription:', message);
      completedTranscription.value += (completedTranscription.value ? ' ' : '') + message.text;
      partialTranscription.value = ''; // Reset partial transcription
    };

    return {
      displayedTranscription,
      isListening,
      handlePartialTranscription,
      handleFinalTranscription,
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

.transcription-text {
  min-height: 100px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>