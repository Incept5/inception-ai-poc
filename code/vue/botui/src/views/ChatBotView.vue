<script setup>
import { ref } from 'vue'
import ChatBot from '../components/ChatBot.vue'
import FileViewer from '../components/FileViewer.vue'
import LoadingBar from '../components/LoadingBar.vue'

const threadId = ref('')
const fileViewerKey = ref(0)
const isLoading = ref(false)

const updateThreadId = (newThreadId) => {
  threadId.value = newThreadId
}

const handleNewMessageDisplayed = () => {
  fileViewerKey.value += 1
}

const setLoading = (value) => {
  isLoading.value = value
}
</script>

<template>
  <div class="content-wrapper">
    <ChatBot
      class="chatbot"
      :initialThreadId="threadId"
      @thread-created="updateThreadId"
      @new-message-displayed="handleNewMessageDisplayed"
      @loading-change="setLoading"
    />
    <FileViewer
      class="file-viewer"
      :threadId="threadId"
      :fileViewerKey="fileViewerKey"
      @loading-change="setLoading"
    />
    <LoadingBar :is-loading="isLoading" />
  </div>
</template>

<style scoped>
.content-wrapper {
  display: flex;
  height: 100%;
  width: 100%;
  position: relative;
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