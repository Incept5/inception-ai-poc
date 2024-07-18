<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  threadId: {
    type: String,
    default: ''
  }
})

const threadInfo = ref({})

const fetchThreadInfo = async () => {
  // TODO: Implement API call to fetch thread information
  // For now, we'll use mock data
  threadInfo.value = {
    id: props.threadId,
    createdAt: new Date().toISOString(),
    messageCount: 10,
    lastActivity: new Date().toISOString()
  }
}

onMounted(() => {
  if (props.threadId) {
    fetchThreadInfo()
  }
})

watch(() => props.threadId, (newThreadId) => {
  if (newThreadId) {
    fetchThreadInfo()
  } else {
    threadInfo.value = {}
  }
})
</script>

<template>
  <div class="info-tab">
    <h2>Thread Information</h2>
    <div v-if="threadId">
      <p><strong>Thread ID:</strong> {{ threadInfo.id }}</p>
      <p><strong>Created At:</strong> {{ new Date(threadInfo.createdAt).toLocaleString() }}</p>
      <p><strong>Message Count:</strong> {{ threadInfo.messageCount }}</p>
      <p><strong>Last Activity:</strong> {{ new Date(threadInfo.lastActivity).toLocaleString() }}</p>
    </div>
    <div v-else>
      <p>No thread selected</p>
    </div>
  </div>
</template>

<style scoped>
.info-tab {
  padding: 1rem;
}

h2 {
  margin-bottom: 1rem;
}

p {
  margin-bottom: 0.5rem;
}
</style>