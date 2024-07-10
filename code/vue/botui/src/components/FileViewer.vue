<script setup>
import { ref, onMounted } from 'vue'
import { fetchFileStructure, fetchFileContent } from '@/api'
import hljs from 'highlight.js'

const fileStructure = ref({})
const selectedFile = ref(null)
const fileContent = ref('')
const highlightedContent = ref('')

const fetchStructure = async () => {
  fileStructure.value = await fetchFileStructure()
  selectFirstFile(fileStructure.value)
}

const selectFirstFile = (structure) => {
  const findFirstFile = (obj) => {
    for (let key in obj) {
      if (typeof obj[key] === 'string') {
        return obj[key]
      } else if (typeof obj[key] === 'object' && obj[key] !== null) {
        const result = findFirstFile(obj[key])
        if (result) return result
      }
    }
    return null
  }

  const firstFile = findFirstFile(structure)
  if (firstFile) {
    selectFile(firstFile)
  }
}

const selectFile = async (filePath) => {
  selectedFile.value = filePath
  fileContent.value = await fetchFileContent(filePath)
  highlightCode()
}

const highlightCode = () => {
  const language = getLanguage(selectedFile.value)
  highlightedContent.value = hljs.highlight(fileContent.value, { language }).value
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
    .then(() => alert('File content copied to clipboard!'))
    .catch(err => console.error('Error copying to clipboard:', err))
}

const downloadFile = () => {
  const blob = new Blob([fileContent.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = getFileName(selectedFile.value)
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
}

onMounted(fetchStructure)
</script>

<template>
  <div class="file-viewer-container">
    <div class="file-tree">
      <h2>Files</h2>
      <ul>
        <li v-for="(value, key) in fileStructure" :key="key">
          <span @click="selectFile(value)" class="file-item">{{ key }}</span>
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
  </div>
</template>

<style scoped>
.file-viewer-container {
  display: flex;
  height: 100%;
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
}

pre {
  margin: 0;
  white-space: pre-wrap;
}
</style>