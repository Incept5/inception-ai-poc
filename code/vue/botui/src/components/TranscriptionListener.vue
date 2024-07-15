<template>
  <div class="transcription-listener">
    <!-- TranscriptionListener component -->
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as assemblyai from 'assemblyai';

export default {
  name: 'TranscriptionListener',
  props: {
    enabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['partial-transcription-received', 'final-transcription-received', 'error'],
  setup(props, { emit }) {
    const error = ref('');
    let rt = null;
    let microphone = null;
    const isInitialized = ref(false);
    const isConnected = ref(false);
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;

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
              if (onAudioCallback && isConnected.value) onAudioCallback(finalBuffer);
            }
          };
        },
        stopRecording() {
          audioContext?.close();
          audioBufferQueue = new Int16Array(0);
        },
        resumeRecording() {
          if (audioContext?.state === 'suspended') {
            audioContext.resume();
          }
        },
      };
    };

    const mergeBuffers = (lhs, rhs) => {
      const mergedBuffer = new Int16Array(lhs.length + rhs.length);
      mergedBuffer.set(lhs, 0);
      mergedBuffer.set(rhs, lhs.length);
      return mergedBuffer;
    };

    const initialize = async () => {
      try {
        microphone = createMicrophone();
        await microphone.requestPermission();

        const response = await fetch("/api/audio-token");
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        rt = new assemblyai.RealtimeService({ token: data.token });

        rt.on("transcript", (message) => {
          console.log("Received transcript message:", message);

          if (message.message_type === 'PartialTranscript') {
            emit('partial-transcription-received', message);
          } else if (message.message_type === 'FinalTranscript') {
            emit('final-transcription-received', message);
          }
        });

        rt.on("error", async (error) => {
          console.error("Transcription error:", error);
          emit('error', error);
          await stopListening();
          attemptReconnect();
        });

        rt.on("close", (event) => {
          console.log("Transcription service closed:", event);
          isConnected.value = false;
          attemptReconnect();
        });

        rt.on("open", () => {
          console.log("WebSocket connection opened");
          isConnected.value = true;
          reconnectAttempts = 0;
        });

        await rt.connect();
        console.log("Connected to AssemblyAI Realtime Service");
        isInitialized.value = true;
        isConnected.value = true;
      } catch (err) {
        error.value = `Error: ${err.message}`;
        console.error(error.value);
        emit('error', error.value);
      }
    };

    const attemptReconnect = async () => {
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})`);
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for 2 seconds before reconnecting
        await initialize();
      } else {
        console.error("Max reconnection attempts reached");
        emit('error', "Unable to establish a stable connection. Please try again later.");
      }
    };

    const startListening = async () => {
      if (!isInitialized.value || !isConnected.value) {
        await initialize();
      }

      if (microphone && rt && isConnected.value) {
        await microphone.startRecording((audioData) => {
          if (isConnected.value) {
            try {
              rt.sendAudio(audioData);
            } catch (err) {
              console.error("Error sending audio:", err);
              emit('error', "Error sending audio data. Attempting to reconnect.");
              attemptReconnect();
            }
          }
        });
        console.log("Started listening");
      } else {
        console.warn("Cannot start listening. Not initialized or not connected.");
        emit('error', "Cannot start listening. Please try again.");
      }
    };

    const stopListening = async () => {
      console.log("Stopping listening");
      if (rt) {
        await rt.close(false);
      }
      if (microphone) {
        microphone.stopRecording();
      }
      isConnected.value = false;
      isInitialized.value = false;
      console.log("Listening stopped");
    };

    watch(() => props.enabled, async (newValue) => {
      if (newValue) {
        await startListening();
      } else {
        await stopListening();
      }
    });

    onMounted(async () => {
      await initialize();
    });

    onUnmounted(async () => {
      await stopListening();
      if (microphone) {
        microphone.stopRecording();
        microphone = null;
      }
      rt = null;
    });

    return {
      error,
    };
  },
};
</script>

<style scoped>
.transcription-listener {
  /* Add any styles if needed */
}
</style>