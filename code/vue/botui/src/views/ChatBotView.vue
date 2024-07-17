<script setup>
import { ref } from 'vue'
import ChatBot from '../components/ChatBot.vue'
import FileViewer from '../components/FileViewer.vue'

const threadId = ref('')
const fileViewerKey = ref(0)

const updateThreadId = (newThreadId) => {
  threadId.value = newThreadId
}

const handleNewMessageDisplayed = () => {
  fileViewerKey.value += 1
}
</script>

<template>
  <div class="content-wrapper">
    <ChatBot
      class="chatbot"
      :initialThreadId="threadId"
      @thread-created="updateThreadId"
      @new-message-displayed="handleNewMessageDisplayed"
    />
    <FileViewer
      class="file-viewer"
      :threadId="threadId"
      :fileViewerKey="fileViewerKey"
    />
  </div>
</template>

<style scoped>
.content-wrapper {
  display: flex;
  height: 100%;
  width: 100%;
}

.chatbot, .file-viewer {
  flex: 1;
  overflow: auto;
  padding: 1rem;
}

.chatbot {
  border-right: 1px solid #ccc;
}
</style>