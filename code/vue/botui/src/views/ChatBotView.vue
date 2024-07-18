<script setup>
import { ref, watch } from 'vue'
import ChatBot from '../components/chatbot/ChatBot.vue'
import FileViewer from '../components/chatbot/FileViewer.vue'
import LoadingBar from '../components/LoadingBar.vue'
import InfoTab from '../components/chatbot/InfoTab.vue'
import OutputTab from '../components/chatbot/OutputTab.vue'

const threadId = ref('')
const fileViewerKey = ref(0)
const isLoading = ref(false)
const activeTab = ref('fileViewer')
const outputUrl = ref('')

const updateThreadId = (newThreadId) => {
  threadId.value = newThreadId
}

const handleNewMessageDisplayed = () => {
  fileViewerKey.value += 1
}

const setLoading = (value) => {
  isLoading.value = value
}

const switchTab = (tabName) => {
  activeTab.value = tabName
}

const handleOutputUrlDetected = (url) => {
  outputUrl.value = url
  activeTab.value = 'output'
}

watch(outputUrl, (newUrl) => {
  if (newUrl) {
    activeTab.value = 'output'
  }
})
</script>

<template>
  <div class="content-wrapper">
    <ChatBot
      class="chatbot"
      :initialThreadId="threadId"
      @thread-created="updateThreadId"
      @new-message-displayed="handleNewMessageDisplayed"
      @loading-change="setLoading"
      @output-url-detected="handleOutputUrlDetected"
    />
    <div class="right-panel">
      <div class="tab-buttons">
        <button
          @click="switchTab('fileViewer')"
          :class="{ active: activeTab === 'fileViewer' }"
        >
          File Viewer
        </button>
        <button
          @click="switchTab('output')"
          :class="{ active: activeTab === 'output' }"
        >
          Output
        </button>
      </div>
      <div class="tab-content">
        <FileViewer
          v-if="activeTab === 'fileViewer'"
          class="file-viewer"
          :threadId="threadId"
          :fileViewerKey="fileViewerKey"
          @loading-change="setLoading"
        />
        <OutputTab
          v-else-if="activeTab === 'output'"
          class="output-tab"
          :url="outputUrl"
        />
      </div>
    </div>
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

.chatbot {
  flex: 1;
  overflow: auto;
  padding: 1rem;
  border-right: 1px solid #ccc;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tab-buttons {
  display: flex;
  border-bottom: 1px solid #ccc;
  background-color: #f5f5f5;
  padding: 0.25rem 0.5rem 0; /* Add padding to the top and sides */
}

.tab-buttons button {
  padding: 0.3rem 1rem; /* Reduce vertical padding to make tabs less high */
  border: none;
  background-color: #4a90e2;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  margin-right: 0.25rem; /* Add some space between tabs */
  margin-bottom: -1px; /* Overlap the bottom border */
}

.tab-buttons button:hover {
  background-color: #3a7bc8;
}

.tab-buttons button.active {
  background-color: #ffffff;
  color: #4a90e2;
  border: 1px solid #ccc;
  border-bottom: 1px solid #ffffff;
}

.tab-content {
  flex: 1;
  overflow: auto;
  background-color: #ffffff;
  border-left: 1px solid #ccc;
  border-right: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
}

.file-viewer, .info-tab {
  height: 100%;
  padding: 1rem;
}

.output-tab {
  height: 100%;
  padding: 1rem;
}
</style>