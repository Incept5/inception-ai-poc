<script>
import { ref, onMounted, onUnmounted } from 'vue';
import * as assemblyai from 'assemblyai';

export default {
  name: 'TranscriptionListener',
  emits: ['partial-transcription-received', 'final-transcription-received'],
  setup(_, { emit }) {
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

    const startListening = async () => {
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
          await stopListening();
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
        console.log("Started listening");
      } catch (err) {
        error.value = `Error: ${err.message}`;
        console.error(error.value);
      }
    };

    const stopListening = async () => {
      console.log("Stopping listening");
      if (rt) {
        await rt.close(false);
        rt = null;
      }
      if (microphone) {
        microphone.stopRecording();
        microphone = null;
      }
      console.log("Listening stopped");
    };

    onMounted(async () => {
      await startListening();
    });

    onUnmounted(async () => {
      await stopListening();
    });

    return {
      error,
    };
  },
};
</script>