<script setup>
// ... (keep the existing script code unchanged)
</script>

<template>
  <div class="chatbot-container">
    <div class="controls">
      <select v-model="botSelector">
        <option v-for="bot in bots" :key="bot.bot_type" :value="bot.bot_type">
          {{ bot.description }}
        </option>
      </select>
      <select v-model="llmSelector" @change="loadModels">
        <option value="anthropic">Anthropic</option>
        <option value="openai">OpenAI</option>
        <option value="ollama">Ollama</option>
        <option value="groq">Groq</option>
      </select>
      <select v-model="modelSelector">
        <option v-for="model in models" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
      <label>
        <input type="checkbox" v-model="showThinking"> Show Thinking
      </label>
      <button @click="initializeThread">New Conversation</button>
    </div>
    <div ref="chatContainer" class="chat-messages">
      <div v-for="(message, index) in messages" :key="index" class="message" :class="message.sender.toLowerCase()">
        <strong>{{ message.sender }}:</strong> {{ message.message }}
      </div>
    </div>
    <div class="input-area">
      <input v-model="userInput" @keyup.enter="handleSendMessage" placeholder="Type your message here...">
      <button @click="handleSendMessage">Send</button>
    </div>
  </div>
</template>

<style scoped>
.chatbot-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 100%;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.controls select,
.controls button,
.controls label {
  flex: 1 1 auto;
  min-width: 120px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 10px;
}

.message {
  margin-bottom: 10px;
  word-wrap: break-word;
  max-width: 100%;
}

.message.you {
  text-align: right;
}

.input-area {
  display: flex;
}

input {
  flex: 1;
  padding: 5px;
  min-width: 0; /* Allow input to shrink below its default size */
}

button {
  padding: 5px 10px;
  background-color: #4a90e2;
  color: white;
  border: none;
  cursor: pointer;
  white-space: nowrap;
}
</style>