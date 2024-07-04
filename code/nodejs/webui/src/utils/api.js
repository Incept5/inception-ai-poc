const API_BASE_URL = 'http://localhost:9871';

export async function fetchBots() {
  const response = await fetch(`${API_BASE_URL}/bots`);
  if (!response.ok) {
    throw new Error('Failed to fetch bots');
  }
  return await response.json();
}

export async function fetchModels(provider) {
  const response = await fetch(`${API_BASE_URL}/llm-models?provider=${provider}`);
  if (!response.ok) {
    throw new Error('Failed to fetch models');
  }
  return await response.json();
}

export async function sendMessageToBot(selectedBot, message, config) {
  const response = await fetch(`${API_BASE_URL}/bots/${selectedBot}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      config,
    }),
  });

  if (!response.ok) {
    throw new Error('API request failed');
  }

  return await response.json();
}