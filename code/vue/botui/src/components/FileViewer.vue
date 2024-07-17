<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { fetchFileStructure, fetchFileContent, updateFiles } from '@/api'
import TreeItem from './TreeItem.vue'
import SourceViewer from './SourceViewer.vue'
import LoadingBar from './LoadingBar.vue'

const toast = useToast()

const props = defineProps({
  threadId: {
    type: String,
    default: ''
  },
  fileViewerKey: {
    type: Number,
    default: 0
  }
})

const fileStructure = ref({})
const selectedFile = ref(null)
const fileContent = ref('')
const error = ref('')
const expandToFirstLeaf = ref(false)

const isLoading = ref(false);
let loadingTimeout;

const setLoading = (value) => {
  clearTimeout(loadingTimeout);
  if (value) {
    isLoading.value = true;
  } else {
    loadingTimeout = setTimeout(() => {
      isLoading.value = false;
    }, 200); // Delay setting isLoading to false to prevent rapid toggling
  }
};

const fetchStructure = async () => {
  console.log('FileViewer: Fetching file structure for threadId:', props.threadId)
  if (!props.threadId) {
    console.log('FileViewer: No threadId provided, resetting component state')
    resetComponentState()
    error.value = 'No thread selected'
    return
  }

  error.value = ''
  setLoading(true);
  console.log('FileViewer: Setting isLoading to true')
  try {
    console.log('FileViewer: Calling fetchFileStructure API...')
    const response = await fetchFileStructure(props.threadId)
    console.log('FileViewer: File structure fetched:', JSON.stringify(response, null, 2))

    const newFileStructure = response.tree || {}

    if (selectedFile.value && !isFileInStructure(selectedFile.value, newFileStructure)) {
      console.log('FileViewer: Currently selected file is no longer in the structure, resetting selection')
      selectedFile.value = null
      fileContent.value = ''
    }

    fileStructure.value = newFileStructure

    expandToFirstLeaf.value = true
  } catch (err) {
    console.error('FileViewer: Error fetching file structure:', err)
    error.value = 'Error fetching file structure. Please try again.'
    resetComponentState()
  } finally {
    setLoading(false);
    console.log('FileViewer: Setting isLoading to false')
  }
}

const resetComponentState = () => {
  fileStructure.value = {}
  selectedFile.value = null
  fileContent.value = ''
  expandToFirstLeaf.value = false
}

const isFileInStructure = (filePath, structure) => {
  for (const [key, value] of Object.entries(structure)) {
    if (typeof value === 'string' && value === filePath) {
      return true
    } else if (typeof value === 'object') {
      if (isFileInStructure(filePath, value)) return true
    }
  }
  return false
}

const selectFirstFile = () => {
  const firstFile = findFirstFile(fileStructure.value)
  if (firstFile) {
    selectFile(firstFile)
  }
}

const findFirstFile = (obj) => {
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      return value
    } else if (typeof value === 'object') {
      const result = findFirstFile(value)
      if (result) return result
    }
  }
  return null
}

const selectFile = async (filePath) => {
  console.log('FileViewer: Selecting file:', filePath)
  selectedFile.value = filePath
  setLoading(true);
  console.log('FileViewer: Setting isLoading to true')
  try {
    console.log('FileViewer: Fetching content for file:', filePath)
    fileContent.value = await fetchFileContent(filePath)
    console.log('FileViewer: File content fetched, length:', fileContent.value.length)
  } catch (err) {
    console.error('FileViewer: Error fetching file content:', err)
    error.value = 'Error fetching file content. Please try again.'
    fileContent.value = ''
  } finally {
    setLoading(false);
    console.log('FileViewer: Setting isLoading to false')
  }
}

const getFileName = (filePath) => filePath.split('/').pop()

const copyToClipboard = () => {
  navigator.clipboard.writeText(fileContent.value)
    .then(() => {
      console.log('File content copied to clipboard')
      toast.success('File content copied to clipboard!', {
        timeout: 2000
      })
    })
    .catch(err => {
      console.error('Error copying to clipboard:', err)
      toast.error('Failed to copy file content. Please try again.', {
        timeout: 3000
      })
    })
}

const downloadFile = () => {
  console.log('Downloading file:', selectedFile.value)
  const blob = new Blob([fileContent.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = getFileName(selectedFile.value)
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  console.log('File download initiated')
  toast.success('File download started', {
    timeout: 2000
  })
}

const refreshFileStructure = () => {
  console.log('Refreshing file structure')
  expandToFirstLeaf.value = false // Reset the expansion state
  fetchStructure()
}

const updateSystem = async () => {
  console.log('FileViewer: Updating system')
  setLoading(true);
  console.log('FileViewer: Setting isLoading to true')
  try {
    await updateFiles(props.threadId)
    console.log('FileViewer: System updated successfully')
    refreshFileStructure()
    toast.success('System updated successfully', {
      timeout: 2000
    })
  } catch (err) {
    console.error('FileViewer: Error updating system:', err)
    error.value = 'Error updating system. Please try again.'
    toast.error('Failed to update system. Please try again.', {
      timeout: 3000
    })
  } finally {
    setLoading(false);
    console.log('FileViewer: Setting isLoading to false')
  }
}

onMounted(() => {
  console.log('FileViewer: Component mounted, threadId:', props.threadId, 'fileViewerKey:', props.fileViewerKey)
  if (props.threadId) {
    fetchStructure()
  }
})

watch([() => props.threadId, () => props.fileViewerKey], ([newThreadId, newFileViewerKey], [oldThreadId, oldFileViewerKey]) => {
  console.log('FileViewer: ThreadId or fileViewerKey changed:', oldThreadId, '->', newThreadId, 'or', oldFileViewerKey, '->', newFileViewerKey)
  fetchStructure()
})
</script>

<template>
  <div class="file-viewer-container">
    <div class="button-row">
      <button @click="refreshFileStructure" title="Refresh file structure" :disabled="isLoading">
        Refresh
      </button>
      <button @click="updateSystem" title="Update System" :disabled="isLoading">
        Update System
      </button>
      <div class="action-buttons" v-if="selectedFile">
        <button @click="copyToClipboard" :disabled="isLoading">Copy</button>
        <button @click="downloadFile" :disabled="isLoading">Download</button>
      </div>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="!props.threadId" class="no-thread-message">No thread selected</div>
    <template v-else>
      <div class="file-tree-and-content">
        <div class="file-tree">
          <h2>Files</h2>
          <div v-if="Object.keys(fileStructure).length === 0" class="no-files-message">
            No files available for this thread.
          </div>
          <TreeItem
            v-else
            :item="fileStructure"
            @select-file="selectFile"
            :expand-to-first-leaf="expandToFirstLeaf"
          />
        </div>
        <SourceViewer
          v-if="selectedFile"
          :file-path="selectedFile"
          :file-content="fileContent"
        />
      </div>
    </template>
    <LoadingBar :is-loading="isLoading" />
  </div>
</template>

<style scoped>
.file-viewer-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;  /* Add this to ensure proper positioning of the LoadingBar */
}

.button-row {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ccc;
  gap: 10px;
}

.action-buttons {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.refresh-icon {
  font-size: 1.2em;
  vertical-align: middle;
}

.file-tree-and-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.file-tree {
  width: 250px;
  min-width: 250px;
  overflow-y: auto;
  border-right: 1px solid #ccc;
  padding: 10px;
}

button {
  padding: 5px 10px;
  background-color: #3490dc; /* Blue background color */
  color: white; /* White text */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s, opacity 0.3s;
}

button:hover {
  background-color: #2779bd; /* Darker blue on hover */
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: red;
  font-weight: bold;
}

.no-thread-message, .no-files-message {
  color: #666;
  font-style: italic;
}
</style>