<template>
  <div class="transcription-view">
    <header>
      <h1 class="header__title">Real-Time Transcription</h1>
      <p class="header__sub-title">
        Try AssemblyAI's new real-time transcription endpoint!
      </p>
    </header>
    <TranscriptionInput v-model="transcriptionText" />
  </div>
</template>

<script>
import { ref } from 'vue';
import TranscriptionInput from '../components/TranscriptionInput.vue';

export default {
  name: 'TranscriptionView',
  components: {
    TranscriptionInput,
  },
  setup() {
    const transcriptionText = ref('');

    return {
      transcriptionText,
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
</style>