import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { fetchBots, fetchModels, sendMessageToBot } from '../utils/api';

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [messageHistory, setMessageHistory] = useState([]);
  const [bots, setBots] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedBot, setSelectedBot] = useState('');
  const [selectedLLM, setSelectedLLM] = useState('anthropic');
  const [selectedModel, setSelectedModel] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchBotsAndModels();
    loadMessageHistory();
  }, []);

  const fetchBotsAndModels = async () => {
    try {
      const botsData = await fetchBots();
      setBots(botsData);
      if (botsData.length > 0) {
        setSelectedBot(botsData[0].bot_type);
        addMessage('System', `Loaded available bots. Default bot: ${botsData[0].description}`);
      }
      await fetchModelsForLLM(selectedLLM);
    } catch (error) {
      console.error('Error fetching bots and models:', error);
      addMessage('System', 'Failed to fetch available bots and models.');
    }
  };

  const fetchModelsForLLM = async (provider) => {
    setIsLoading(true);
    addMessage('System', `Fetching models for ${provider}...`);
    try {
      const data = await fetchModels(provider);
      if (data.models && data.models.length > 0) {
        setModels(data.models);
        setSelectedModel(data.models[0]);
        addMessage('System', `Loaded ${data.models.length} models for ${provider}. Selected model: ${data.models[0]}`);
      } else {
        addMessage('System', `No models found for ${provider}.`);
      }
    } catch (error) {
      console.error('Error fetching models:', error);
      addMessage('System', `Failed to fetch models for ${provider}.`);
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = (sender, message) => {
    setMessages(prev => [...prev, { sender, message }]);
  };

  const updateMessageHistory = (message) => {
    if (!messageHistory.includes(message)) {
      const updatedHistory = [message, ...messageHistory.slice(0, 9)];
      setMessageHistory(updatedHistory);
      localStorage.setItem('messageHistory', JSON.stringify(updatedHistory));
    }
  };

  const loadMessageHistory = () => {
    const savedHistory = localStorage.getItem('messageHistory');
    if (savedHistory) {
      setMessageHistory(JSON.parse(savedHistory));
    }
  };

  const sendMessage = async () => {
    if (!userInput.trim()) return;

    addMessage('You', userInput);
    updateMessageHistory(userInput);
    setUserInput('');
    setIsLoading(true);

    try {
      const data = await sendMessageToBot(selectedBot, userInput, {
        llm_provider: selectedLLM,
        llm_model: selectedModel
      });
      addMessage(`${selectedBot} Bot (${selectedLLM} - ${selectedModel})`, data.response);
    } catch (error) {
      console.error('Error:', error);
      addMessage('System', 'An error occurred while communicating with the chatbot.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 min-h-screen">
      <Head>
        <title>Inception AI Chatbot</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="bg-white shadow-md rounded-lg p-6 mb-8">
          <h1 className="text-4xl font-bold text-center text-gray-800">
            Inception AI Chatbot
          </h1>
        </header>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div
            id="chat-container"
            className="chat-container overflow-y-auto mb-6 p-4 bg-gray-50 rounded-lg shadow-inner"
            style={{height: 'calc(100vh - 400px)', minHeight: '300px'}}
          >
            {messages.map((msg, index) => (
              <div key={index} className={`mb-4 ${msg.sender === 'You' ? 'text-right' : 'text-left'}`}>
                <span className={`inline-block p-3 rounded-lg max-w-xs lg:max-w-md ${
                  msg.sender === 'You'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}>
                  <strong className="font-semibold">{msg.sender}:</strong> {msg.message}
                </span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-4 mb-4">
            <div className="flex items-center">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                className="flex-grow p-3 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Type your message here..."
                list="message-history"
              />
              <datalist id="message-history">
                {messageHistory.map((msg, index) => (
                  <option key={index} value={msg} />
                ))}
              </datalist>
              <button
                onClick={sendMessage}
                className="bg-blue-500 text-white p-3 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150 ease-in-out"
              >
                Send
              </button>
              {isLoading && (
                <div className="ml-3 animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <select
                value={selectedLLM}
                onChange={(e) => {
                  setSelectedLLM(e.target.value);
                  fetchModelsForLLM(e.target.value);
                }}
                className="col-span-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="anthropic">Anthropic</option>
                <option value="openai">OpenAI</option>
                <option value="ollama">Ollama</option>
                <option value="groq">Groq</option>
              </select>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="col-span-3 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {models.map((model, index) => (
                  <option key={index} value={model}>{model}</option>
                ))}
              </select>
            </div>

            <select
              value={selectedBot}
              onChange={(e) => {
                setSelectedBot(e.target.value);
                addMessage('System', `Switched to ${e.target.options[e.target.selectedIndex].text}.`);
              }}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {bots.map((bot, index) => (
                <option key={index} value={bot.bot_type}>{bot.description}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}