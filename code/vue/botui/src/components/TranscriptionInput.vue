<template>
  <div class="transcription-input">
    <textarea
      v-model="transcriptionText"
      class="transcription-input__textarea"
      placeholder="Transcription will appear here..."
      rows="5"
    ></textarea>
    <button
      @click="toggleRecording"
      class="transcription-input__button"
      :disabled="isLoading"
    >
      {{ isRecording ? "Stop Recording" : "Start Recording" }}
    </button>
    <p v-if="error" class="transcription-input__error">{{ error }}</p>
  </div>
</template>

<script>
import { ref, onUnmounted } from 'vue';
import * as assemblyai from 'assemblyai';

export default {
  name: 'TranscriptionInput',
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: String,
      default: '',
    },
  },
  setup(props, { emit }) {
    const isRecording = ref(false);
    const isLoading = ref(false);
    const transcriptionText = ref(props.modelValue);
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
      let lastMessageEnd = 0;

      rt.on("transcript", (message) => {
        console.log("Received transcript message:", message);
        console.log("Current transcriptionText:", transcriptionText.value);

        if (message.message_type === 'PartialTranscript' || message.message_type === 'FinalTranscript') {
          if (message.audio_start >= lastMessageEnd) {
            // This is a new segment of speech
            console.log("New segment detected. Appending text.");
            transcriptionText.value += (transcriptionText.value ? ' ' : '') + message.text;
          } else {
            // This is an update to the previous segment
            console.log("Updating previous segment.");
            const lastSpace = transcriptionText.value.lastIndexOf(' ');
            if (lastSpace !== -1) {
              transcriptionText.value = transcriptionText.value.substring(0, lastSpace) + ' ' + message.text;
            } else {
              transcriptionText.value = message.text;
            }
          }
          lastMessageEnd = message.audio_end;
          console.log("Updated transcriptionText:", transcriptionText.value);
          emit('update:modelValue', transcriptionText.value);
        }
      });

      rt.on("error", async (error) => {
        console.error("Transcription error:", error);
        await stopRecording();
        throw new Error("Transcription error occurred");
      });

      rt.on("close", (event) => {
        console.log("Transcription service closed:", event);
        rt = null;
      });

      await rt.connect();
      console.log("Connected to AssemblyAI Realtime Service");
      await microphone.startRecording((audioData) => {
        rt.sendAudio(audioData);
      });
      console.log("Started recording");
    };

    const stopRecording = async () => {
      console.log("Stopping recording");
      if (rt) {
        await rt.close(false);
        rt = null;
      }
      if (microphone) {
        microphone.stopRecording();
        microphone = null;
      }
      console.log("Recording stopped");
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
.transcription-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.transcription-input__textarea {
  width: 100%;
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.transcription-input__button {
  align-self: flex-start;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  cursor: pointer;
  border-radius: 5px;
  font-size: 1em;
  border: none;
}

.transcription-input__button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.transcription-input__error {
  color: #ff0000;
  font-weight: bold;
}
</style>