<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { fetchFileStructure, fetchFileContent, updateFiles, getFileUrl } from '@/api'
import TreeItem from './TreeItem.vue'
import SourceViewer from './SourceViewer.vue'
import './css/FileViewer.css'

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

const emit = defineEmits(['loading-change'])

const fileList = ref([])
const treeStructure = ref({})
const selectedFile = ref(null)
const fileContent = ref('')
const error = ref('')
const expandToFirstLeaf = ref(false)

const isLoading = ref(false)
let loadingTimeout

// New refs for resizable panels
const fileTreePanel = ref(null)
const resizer = ref(null)
const fileTreeWidth = ref(250) // Initial width of the file tree panel

const setLoading = (value) => {
  clearTimeout(loadingTimeout)
  if (value) {
    isLoading.value = true
    emit('loading-change', true)
  } else {
    loadingTimeout = setTimeout(() => {
      isLoading.value = false
      emit('loading-change', false)
    }, 200)
  }
}

const fetchStructure = async () => {
  console.log('FileViewer: Fetching file structure for threadId:', props.threadId)
  if (!props.threadId) {
    console.log('FileViewer: No threadId provided, resetting component state')
    resetComponentState()
    error.value = 'No thread selected'
    return
  }

  error.value = ''
  setLoading(true)
  console.log('FileViewer: Setting isLoading to true')
  try {
    console.log('FileViewer: Calling fetchFileStructure API...')
    const response = await fetchFileStructure(props.threadId)
    console.log('FileViewer: File structure fetched:', JSON.stringify(response, null, 2))

    fileList.value = response.files || []
    treeStructure.value = buildTreeStructure(fileList.value)

    if (selectedFile.value && !isFileInStructure(selectedFile.value, treeStructure.value)) {
      console.log('FileViewer: Currently selected file is no longer in the structure, resetting selection')
      selectedFile.value = null
      fileContent.value = ''
    }

    expandToFirstLeaf.value = true
  } catch (err) {
    console.error('FileViewer: Error fetching file structure:', err)
    error.value = 'Error fetching file structure. Please try again.'
    resetComponentState()
  } finally {
    setLoading(false)
    console.log('FileViewer: Setting isLoading to false')
  }
}

const resetComponentState = () => {
  fileList.value = []
  treeStructure.value = {}
  selectedFile.value = null
  fileContent.value = ''
  expandToFirstLeaf.value = false
}

const buildTreeStructure = (files) => {
  const tree = {}
  const prefix = `__threads/${props.threadId}/`
  files.forEach(file => {
    const strippedPath = file.path.startsWith(prefix) ? file.path.slice(prefix.length) : file.path
    const parts = strippedPath.split('/')
    let current = tree
    parts.forEach((part, index) => {
      if (index === parts.length - 1) {
        current[part] = { ...file, type: 'file', path: strippedPath }
      } else {
        if (!current[part]) {
          current[part] = { type: 'directory', children: {} }
        }
        current = current[part].children
      }
    })
  })
  return tree
}

const isFileInStructure = (filePath, structure) => {
  const prefix = `__threads/${props.threadId}/`
  const strippedPath = filePath.startsWith(prefix) ? filePath.slice(prefix.length) : filePath
  const parts = strippedPath.split('/')
  let current = structure
  for (const part of parts) {
    if (!current[part]) return false
    current = current[part].children || current[part]
  }
  return true
}

const selectFirstFile = () => {
  const firstFile = findFirstFile(treeStructure.value)
  if (firstFile) {
    selectFile(firstFile.path)
  }
}

const findFirstFile = (obj) => {
  for (const [key, value] of Object.entries(obj)) {
    if (value.type === 'file') {
      return value
    } else if (value.type === 'directory') {
      const result = findFirstFile(value.children)
      if (result) return result
    }
  }
  return null
}

const selectFile = async (filePath) => {
  console.log('FileViewer: Selecting file:', filePath)
  selectedFile.value = filePath
  setLoading(true)
  console.log('FileViewer: Setting isLoading to true')
  try {
    console.log('FileViewer: Fetching content for file:', filePath)
    const fullPath = `__threads/${props.threadId}/${filePath}`
    fileContent.value = await fetchFileContent(fullPath)
    console.log('FileViewer: File content fetched, length:', fileContent.value.length)
  } catch (err) {
    console.error('FileViewer: Error fetching file content:', err)
    error.value = 'Error fetching file content. Please try again.'
    fileContent.value = ''
  } finally {
    setLoading(false)
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
  setLoading(true)
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
    setLoading(false)
    console.log('FileViewer: Setting isLoading to false')
  }
}

// New function to handle panel resizing
const initResize = (e) => {
  window.addEventListener('mousemove', resize)
  window.addEventListener('mouseup', stopResize)
}

const resize = (e) => {
  const newWidth = e.clientX - fileTreePanel.value.getBoundingClientRect().left
  if (newWidth >= 250) {
    fileTreeWidth.value = newWidth
  }
}

const stopResize = () => {
  window.removeEventListener('mousemove', resize)
  window.removeEventListener('mouseup', stopResize)
}

// Update the openFileInNewTab function
const openFileInNewTab = () => {
  if (selectedFile.value) {
    const fileUrl = getFileUrl(props.threadId, selectedFile.value)
    window.open(fileUrl, '_blank')
    console.log('File opened in new tab')
    toast.success('File opened in new tab', {
      timeout: 2000
    })
  }
}

onMounted(() => {
  console.log('FileViewer: Component mounted, threadId:', props.threadId, 'fileViewerKey:', props.fileViewerKey)
  if (props.threadId) {
    fetchStructure()
  }
  
  // Set up resizer event listener
  if (resizer.value) {
    resizer.value.addEventListener('mousedown', initResize)
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
        <button @click="openFileInNewTab" :disabled="isLoading">Open</button>
      </div>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="!props.threadId" class="no-thread-message">No thread selected</div>
    <template v-else>
      <div class="file-tree-and-content">
        <div class="file-tree" ref="fileTreePanel" :style="{ width: `${fileTreeWidth}px` }">
          <h2>Files</h2>
          <div v-if="Object.keys(treeStructure).length === 0" class="no-files-message">
            No files available for this thread.
          </div>
          <TreeItem
            v-else
            :item="treeStructure"
            @select-file="selectFile"
            :expand-to-first-leaf="expandToFirstLeaf"
          />
        </div>
        <div class="resizer" ref="resizer"></div>
        <SourceViewer
          v-if="selectedFile"
          :file-path="selectedFile"
          :file-content="fileContent"
        />
      </div>
    </template>
  </div>
</template>