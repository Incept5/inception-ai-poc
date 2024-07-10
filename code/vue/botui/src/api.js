import axios from 'axios'

const API_BASE_URL = 'http://localhost:9870/api'

export const fetchBots = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/bots`)
    return response.data
  } catch (error) {
    console.error('Error fetching bots:', error)
    return []
  }
}

export const fetchModels = async (provider) => {
  if (!provider) {
    console.warn('Provider is null or undefined. Returning empty array.')
    return []
  }
  try {
    const response = await axios.get(`${API_BASE_URL}/llm-models?provider=${provider}`)
    return response.data.models
  } catch (error) {
    console.error(`Error fetching models for ${provider}:`, error)
    return []
  }
}

export const sendMessage = async (bot, message, llmProvider, llmModel, threadId) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/bots/${bot}`,
      {
        message,
        config: {
          llm_provider: llmProvider,
          llm_model: llmModel,
          thread_id: threadId
        }
      },
      { responseType: 'stream' }
    )
    return response.data
  } catch (error) {
    console.error('Error sending message:', error)
    throw error
  }
}

export const fetchFileStructure = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/files`)
    return response.data
  } catch (error) {
    console.error('Error fetching file structure:', error)
    return {}
  }
}

export const fetchFileContent = async (filePath) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/file/${encodeURIComponent(filePath)}`, { responseType: 'text' })
    return response.data
  } catch (error) {
    console.error('Error fetching file content:', error)
    return 'Error loading file content'
  }
}