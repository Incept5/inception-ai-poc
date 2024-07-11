import axios from 'axios'

const API_BASE_URL = '/api' // nginx should proxy this to the backend when running a dev server at http://localhost:5173/

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
    const response = await axios.get(`${API_BASE_URL}/llm-models`, {
      params: { provider: provider.toLowerCase() }
    })
    return response.data.models
  } catch (error) {
    console.error(`Error fetching models for ${provider}:`, error)
    return []
  }
}

export const sendMessage = async (bot, message, llmProvider, llmModel, threadId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/bots/${bot}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          config: {
            llm_provider: llmProvider,
            llm_model: llmModel,
            thread_id: threadId
          }
        }),
      }
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let partialChunk = ''

    return {
      async *[Symbol.asyncIterator]() {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = partialChunk + decoder.decode(value, { stream: true })
          const events = chunk.split('\n\n')
          partialChunk = events.pop() || ''

          for (const event of events) {
            if (event.startsWith('data: ')) {
              const jsonData = event.slice(6)
              if (jsonData === '[DONE]') {
                return
              }
              try {
                const parsedData = JSON.parse(jsonData)
                yield parsedData
              } catch (e) {
                console.error('Error parsing JSON:', e)
              }
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('Error sending message:', error)
    throw error
  }
}

export const fetchFileStructure = async (threadId) => {
  // Check if the threadId is valid before making the request
  if (!threadId || threadId === 'undefined') {
    return {}
  }

  try {
    const response = await fetch(`${API_BASE_URL}/files/__threads/${threadId}`)
    if (response.ok) {
      return await response.json()
    } else if (response.status === 404) {
      // Return an empty object for 404 errors without logging
      return {}
    } else {
      // For other errors, log and return an empty object
      console.error('Error fetching file structure:', response.statusText)
      return {}
    }
  } catch (error) {
    // For network errors, log and return an empty object
    console.error('Network error fetching file structure:', error)
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

export const updateFiles = async (threadId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/update_files/__threads/${threadId}`)
    return response.data
  } catch (error) {
    console.error('Error updating files:', error)
    throw error
  }
}