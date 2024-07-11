<script setup>
import { ref, onMounted, watch } from 'vue'
import { fetchFileStructure, fetchFileContent } from '@/api'
import hljs from 'highlight.js'

const props = defineProps({
  threadId: {
    type: String,
    default: ''
  }
})

const fileStructure = ref({})
const selectedFile = ref(null)
const fileContent = ref('')
const highlightedContent = ref('')
const error = ref('')

const fetchStructure = async () => {
  console.log('Fetching file structure for threadId:', props.threadId)
  if (!props.threadId) {
    console.log('No threadId provided, resetting component state')
    resetComponentState()
    error.value = 'No thread selected'
    return
  }

  error.value = ''
  try {
    console.log('Calling fetchFileStructure API...')
    const newFileStructure = await fetchFileStructure(props.threadId)
    console.log('File structure fetched:', JSON.stringify(newFileStructure, null, 2))

    // Check if the currently selected file is still present in the new structure
    if (selectedFile.value && !isFileInStructure(selectedFile.value, newFileStructure)) {
      console.log('Currently selected file is no longer in the structure, resetting selection')
      selectedFile.value = null
      fileContent.value = ''
      highlightedContent.value = ''
    }

    fileStructure.value = newFileStructure

    // If no file is selected (either because it was reset or not selected before), select the first file
    if (!selectedFile.value) {
      selectFirstFile()
    }
  } catch (err) {
    console.error('Error fetching file structure:', err)
    error.value = 'Error fetching file structure. Please try again.'
    resetComponentState()
  }
}

const resetComponentState = () => {
  fileStructure.value = {}
  selectedFile.value = null
  fileContent.value = ''
  highlightedContent.value = ''
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
  console.log('Selecting file:', filePath)
  selectedFile.value = filePath
  try {
    console.log('Fetching content for file:', filePath)
    fileContent.value = await fetchFileContent(filePath)
    console.log('File content fetched, length:', fileContent.value.length)
    highlightCode()
  } catch (err) {
    console.error('Error fetching file content:', err)
    error.value = 'Error fetching file content. Please try again.'
    fileContent.value = ''
    highlightedContent.value = ''
  }
}

const highlightCode = () => {
  console.log('Highlighting code for file:', selectedFile.value)
  const language = getLanguage(selectedFile.value)
  highlightedContent.value = hljs.highlight(fileContent.value, { language }).value
  console.log('Code highlighted, length:', highlightedContent.value.length)
}

const getLanguage = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase()
  const languageMap = {
    'js': 'javascript',
    'py': 'python',
    'html': 'html',
    'css': 'css',
    'json': 'json',
    'md': 'markdown',
    'java': 'java',
  }
  return languageMap[extension] || 'plaintext'
}

const getFileName = (filePath) => filePath.split('/').pop()

const copyToClipboard = () => {
  navigator.clipboard.writeText(fileContent.value)
    .then(() => {
      console.log('File content copied to clipboard')
      alert('File content copied to clipboard!')
    })
    .catch(err => console.error('Error copying to clipboard:', err))
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
}

const refreshFileStructure = () => {
  console.log('Refreshing file structure')
  fetchStructure()
}

onMounted(() => {
  console.log('FileViewer component mounted, threadId:', props.threadId)
  if (props.threadId) {
    fetchStructure()
  }
})

watch(() => props.threadId, (newThreadId, oldThreadId) => {
  console.log('ThreadId changed:', oldThreadId, '->', newThreadId)
  fetchStructure()
})
</script>

<template>
  <div class="file-viewer-container">
    <div class="button-row">
      <button @click="refreshFileStructure" title="Refresh file structure">
        <span class="refresh-icon">&#x21bb;</span> Refresh
      </button>
      <!-- Add more buttons here if needed -->
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="!props.threadId" class="no-thread-message">No thread selected</div>
    <template v-else>
      <div class="file-tree">
        <h2>Files</h2>
        <div v-if="Object.keys(fileStructure).length === 0" class="no-files-message">
          No files available for this thread.
        </div>
        <ul v-else>
          <li v-for="(value, key) in fileStructure" :key="key">
            <span class="folder-item">{{ key }}</span>
            <ul>
              <template v-if="typeof value === 'object'">
                <li v-for="(subValue, subKey) in value" :key="subKey">
                  <span v-if="typeof subValue === 'string'" @click="selectFile(subValue)" class="file-item">{{ subKey }}</span>
                  <template v-else>
                    <span class="folder-item">{{ subKey }}</span>
                    <ul>
                      <li v-for="(leafValue, leafKey) in subValue" :key="leafKey">
                        <span v-if="typeof leafValue === 'string'" @click="selectFile(leafValue)" class="file-item">{{ leafKey }}</span>
                        <template v-else>
                          <span class="folder-item">{{ leafKey }}</span>
                          <ul>
                            <li v-for="(finalValue, finalKey) in leafValue" :key="finalKey">
                              <span @click="selectFile(finalValue)" class="file-item">{{ finalKey }}</span>
                            </li>
                          </ul>
                        </template>
                      </li>
                    </ul>
                  </template>
                </li>
              </template>
              <li v-else>
                <span @click="selectFile(value)" class="file-item">{{ key }}</span>
              </li>
            </ul>
          </li>
        </ul>
      </div>
      <div v-if="selectedFile" class="file-content">
        <div class="file-name">
          {{ getFileName(selectedFile) }}
        </div>
        <div class="action-buttons">
          <button @click="copyToClipboard">Copy</button>
          <button @click="downloadFile">Download</button>
        </div>
        <pre><code v-html="highlightedContent"></code></pre>
      </div>
    </template>
  </div>
</template>

<style scoped>
.file-viewer-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.button-row {
  padding: 10px;
  border-bottom: 1px solid #ccc;
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
  width: 200px;
  overflow-y: auto;
  border-right: 1px solid #ccc;
  padding: 10px;
}

.file-item {
  cursor: pointer;
}

.file-item:hover {
  text-decoration: underline;
}

.file-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.file-name {
  font-weight: bold;
  margin-bottom: 10px;
}

.action-buttons {
  margin-bottom: 10px;
}

button {
  margin-right: 10px;
  padding: 5px 10px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #e0e0e0;
}

pre {
  margin: 0;
  white-space: pre-wrap;
}

.error-message {
  color: red;
  font-weight: bold;
}

.no-thread-message, .no-files-message {
  color: #666;
  font-style: italic;
}

.folder-item {
  font-weight: bold;
}
</style>