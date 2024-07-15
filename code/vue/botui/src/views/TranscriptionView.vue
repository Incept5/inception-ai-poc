<template>
  <div class="transcription-view">
    <header>
      <h1 class="header__title">Real-Time Transcription</h1>
      <p class="header__sub-title">
        Try AssemblyAI's new real-time transcription endpoint!
      </p>
    </header>
    <div class="real-time-interface">
      <p id="real-time-title" class="real-time-interface__title">
        {{ isRecording ? "Click stop to end recording!" : "Click start to begin recording!" }}
      </p>
      <button @click="toggleRecording" class="real-time-interface__button" :disabled="isLoading">
        {{ isRecording ? "Stop" : "Start" }}
      </button>
      <p v-if="isRecording" class="real-time-interface__message">{{ transcriptionText }}</p>
      <p v-if="error" class="real-time-interface__error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import * as assemblyai from 'assemblyai';

export default {
  name: 'TranscriptionView',
  setup() {
    const isRecording = ref(false);
    const isLoading = ref(false);
    const transcriptionText = ref('');
    const error = ref('');
    let rt = null;
    let microphone = null;

    const createMicrophone = () => {
      let stream;
      let audioContext;
      let audioWorkletNode;
      let source;
      let audioBufferQueue = new Int16Array(0);

      return {
        async requestPermission() {
          try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          } catch (err) {
            throw new Error('Microphone permission denied');
          }
        },
        async startRecording(onAudioCallback) {
          if (!stream) await this.requestPermission();
          audioContext = new AudioContext({
            sampleRate: 16000,
            latencyHint: 'balanced'
          });
          source = audioContext.createMediaStreamSource(stream);
          await audioContext.audioWorklet.addModule('/botui/audio-processor.js');
          audioWorkletNode = new AudioWorkletNode(audioContext, 'audio-processor');
          source.connect(audioWorkletNode);
          audioWorkletNode.connect(audioContext.destination);
          audioWorkletNode.port.onmessage = (event) => {
            const currentBuffer = new Int16Array(event.data.audio_data);
            audioBufferQueue = mergeBuffers(audioBufferQueue, currentBuffer);
            const bufferDuration = (audioBufferQueue.length / audioContext.sampleRate) * 1000;
            if (bufferDuration >= 100) {
              const totalSamples = Math.floor(audioContext.sampleRate * 0.1);
              const finalBuffer = new Uint8Array(audioBufferQueue.subarray(0, totalSamples).buffer);
              audioBufferQueue = audioBufferQueue.subarray(totalSamples);
              if (onAudioCallback) onAudioCallback(finalBuffer);
            }
          };
        },
        stopRecording() {
          stream?.getTracks().forEach((track) => track.stop());
          audioContext?.close();
          audioBufferQueue = new Int16Array(0);
        }
      };
    };

    const mergeBuffers = (lhs, rhs) => {
      const mergedBuffer = new Int16Array(lhs.length + rhs.length);
      mergedBuffer.set(lhs, 0);
      mergedBuffer.set(rhs, lhs.length);
      return mergedBuffer;
    };

    const toggleRecording = async () => {
      isLoading.value = true;
      error.value = '';

      try {
        if (isRecording.value) {
          await stopRecording();
        } else {
          await startRecording();
        }
        isRecording.value = !isRecording.value;
      } catch (err) {
        error.value = `Error: ${err.message}`;
      } finally {
        isLoading.value = false;
      }
    };

    const startRecording = async () => {
      microphone = createMicrophone();
      await microphone.requestPermission();

      const response = await fetch("/api/audio-token");
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }

      rt = new assemblyai.RealtimeService({ token: data.token });
      const texts = {};

      rt.on("transcript", (message) => {
        texts[message.audio_start] = message.text;
        const keys = Object.keys(texts);
        keys.sort((a, b) => a - b);
        let msg = "";
        for (const key of keys) {
          if (texts[key]) {
            msg += ` ${texts[key]}`;
          }
        }
        transcriptionText.value = msg;
      });

      rt.on("error", async (error) => {
        console.error(error);
        await stopRecording();
        throw new Error("Transcription error occurred");
      });

      rt.on("close", (event) => {
        console.log(event);
        rt = null;
      });

      await rt.connect();
      await microphone.startRecording((audioData) => {
        rt.sendAudio(audioData);
      });
    };

    const stopRecording = async () => {
      if (rt) {
        await rt.close(false);
        rt = null;
      }
      if (microphone) {
        microphone.stopRecording();
        microphone = null;
      }
    };

    onUnmounted(async () => {
      await stopRecording();
    });

    return {
      isRecording,
      isLoading,
      transcriptionText,
      error,
      toggleRecording,
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

.real-time-interface__title {
  font-size: 1.5em;
  margin-bottom: 20px;
}

.real-time-interface__button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  font-size: 1.2em;
  border: none;
}

.real-time-interface__button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.real-time-interface__message {
  margin-top: 20px;
  font-size: 1.2em;
  white-space: pre-wrap;
}

.real-time-interface__error {
  margin-top: 20px;
  color: #ff0000;
  font-weight: bold;
}
</style>