<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import ChatBot from './components/ChatBot.vue'
import FileViewer from './components/FileViewer.vue'

const router = useRouter()
const route = useRoute()

const threadId = ref('')
const fileViewerKey = ref(0)

const updateThreadId = (newThreadId) => {
  threadId.value = newThreadId
  router.push({ name: 'thread', params: { threadId: newThreadId } })
}

const handleNewMessageDisplayed = () => {
  fileViewerKey.value += 1
}

onMounted(() => {
  if (route.params.threadId) {
    threadId.value = route.params.threadId
  }
})

watch(() => route.params.threadId, (newThreadId) => {
  if (newThreadId) {
    threadId.value = newThreadId
  }
})
</script>

<template>
  <div class="app-container">
    <header>
      <h1>Inception AI Chatbot</h1>
    </header>
    <main>
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
    </main>
  </div>
</template>

<style>
/* Reset default margins and paddings */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

body {
  font-family: Arial, sans-serif;
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

header {
  background-color: #4a90e2;
  color: white;
  padding: 1rem;
  text-align: center;
}

main {
  flex: 1;
  overflow: hidden;
}

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