class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Float32Array(128);
    this._bytesWritten = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (input.length > 0) {
      const channel = input[0];
      for (let i = 0; i < channel.length; i++) {
        this._buffer[this._bytesWritten++] = channel[i];
        if (this._bytesWritten === this._buffer.length) {
          const int16Buffer = new Int16Array(this._buffer.length);
          for (let j = 0; j < this._buffer.length; j++) {
            int16Buffer[j] = Math.max(-1, Math.min(1, this._buffer[j])) * 0x7fff;
          }
          this.port.postMessage({
            audio_data: int16Buffer.buffer,
          });
          this._bytesWritten = 0;
        }
      }
    }
    return true;
  }
}

registerProcessor("audio-processor", AudioProcessor);