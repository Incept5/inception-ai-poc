<script setup>
import { ref } from 'vue'

const props = defineProps({
  filePath: {
    type: String,
    required: true
  },
  fileContent: {
    type: String,
    required: true
  }
})

const getFileName = (filePath) => filePath.split('/').pop()
</script>

<template>
  <div class="source-viewer">
    <div class="file-name">
      {{ getFileName(props.filePath) }}
    </div>
    <div class="text-container">
      <textarea
        :value="props.fileContent"
        readonly
        spellcheck="false"
        wrap="off"
      ></textarea>
    </div>
  </div>
</template>

<style scoped>
.source-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%; /* Ensure the component takes up full width */
  overflow: hidden;
}

.file-name {
  font-weight: bold;
  padding: 10px;
  background-color: #f0f0f0;
  border-bottom: 1px solid #ccc;
}

.text-container {
  flex: 1;
  overflow: hidden;
  display: flex; /* Add flexbox to ensure textarea fills the container */
}

textarea {
  flex: 1; /* Make textarea grow to fill available space */
  width: 100%;
  height: 100%;
  padding: 10px;
  border: none;
  resize: none;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #f8f8f8;
  color: #333;
  overflow-y: auto;
  white-space: pre;
  box-sizing: border-box; /* Ensure padding is included in the width/height */
}
</style>