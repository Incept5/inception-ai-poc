# Inception AI Chatbot Project

This is a playground project for experimenting with different AI models and chatbot configurations. The project consists of a simple web interface for interacting with a chatbot server running in a Docker container.

The UI allows you to change the following:

* Which bot you are talking to
  * You can add new bots under /code/python/py-server/bots/
  * Make sure you also add that bot to /code/python/py-server/bots/configured_bots.py
* Which LLM Provider you are using
  * Local or remote Ollama (via OLLAMA_BASE_URL in .env)
  * Anthropic Claude
  * Open AI
  * Groq
* Which LLM model you are using
  * Will query Ollama for the list of installed models

![docs/images/inception-ui.png](docs/images/inception-ui.png)

# Example Bots

The project includes several specialized bots, each designed for specific tasks:

* File Saving Bot - [code/python/aiserver/bots/file_saving_bot.py](code/python/aiserver/bots/file_saving_bot.py)
  * A bot that can engage in conversations and save generated files
  * Useful for creating and storing code snippets, configurations, or other text-based files during interactions
* System Improver Bot - [code/python/aiserver/bots/system_improver_bot.py](code/python/aiserver/bots/system_improver_bot.py)
  * Specialized in analyzing and suggesting improvements for software systems
  * Can review system structures, answer questions about the system, and propose enhancements
  * Has access to file content and can generate or modify code snippets
* Web App Bot - [code/python/aiserver/bots/web_app_bot.py](code/python/aiserver/bots/web_app_bot.py)
  * Focused on creating single HTML file web applications
  * Can generate complete, self-contained HTML files with embedded CSS and JavaScript
  * Implements modern web development practices and responsive design
* Simple Bot - [code/python/aiserver/bots/simple_bot.py](code/python/aiserver/bots/simple_bot.py)
  * A basic Langgraph bot without any additional tools
  * Suitable for general conversations and simple queries
* Web Search Bot - [code/python/aiserver/bots/web_search_bot.py](code/python/aiserver/bots/web_search_bot.py)
  * A Langgraph bot equipped with a web search tool
  * Capable of providing information from the internet to answer queries
* Ollama Bot - [code/python/aiserver/bots/ollama_bot.py](code/python/aiserver/bots/ollama_bot.py)
  * A bot that interacts directly with Ollama models
  * Does not use the Langchain framework, providing a different approach to bot interactions

Each bot is designed to showcase different capabilities and use cases within the Inception AI Chatbot Project.

## Project Structure

```
.
├── code
│   ├── python
│   │   └── aiserver
│   │       ├── bots
│   │       ├── llms
│   │       ├── mylangchain
│   │       ├── playground
│   │       ├── processors
│   │       ├── routes
│   │       ├── tools
│   │       └── utils
│   ├── web
│   │   └── www
│   │       ├── chatbot
│   │       └── file-viewer
│   └── webapp
├── data
│   └── persisted_files
├── docker
└── docs
    └── images
```

## Prerequisites

- Docker and Docker Compose
- Git

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a `.env` file in the root directory based on `.example.env`:
   ```
   cp .example.env .env
   ```

3. Edit the `.env` file and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   LANGSMITH_API_KEY=your_langsmith_api_key_here
   ```

## Building and Running

1. Navigate to the `docker` directory:
   ```
   cd docker
   ```

2. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

   This command will build the Python server image and start the container. The server will be accessible at `http://localhost:9871`.

3. To stop the containers, use:
   ```
   docker-compose down
   ```

## Using the Chatbot

1. Open the [http://localhost:9870/chatbot/index.html](http://localhost:9870/chatbot/index.html) file in a web browser.

2. You should see a simple interface where you can type messages and receive responses from the chatbot.

3. The client will communicate with the server running at `http://localhost:9871`.

## Development

- The main server code is located in `code/python/py-server/server.py`.
- To modify the Python dependencies, update `code/python/py-server/requirements.txt`.
- The Gunicorn configuration is in `code/python/py-server/gunicorn.conf.py`.
- To modify the Docker setup, edit `docker/Dockerfile.python-server` and `docker/docker-compose.yml`.

### Auto-reloading during development

The server is configured to auto-reload when code changes are detected. This means that most changes you make to the Python files will be reflected immediately without needing to rebuild or restart the Docker container.

To take advantage of this:

1. Make sure your Docker container is running (`docker-compose up`).
2. Edit the Python files in the `code/python/py-server` directory.
3. Save your changes.
4. The server should automatically detect the changes and restart.

Note: While code changes will trigger a reload, any in-memory data or state will be lost during this process. This includes any ongoing conversations or temporary data not stored in a persistent database.

For changes to requirements or Docker configuration, you will still need to rebuild and restart the container:

```
docker-compose down
docker-compose up --build
```

## Troubleshooting

- If you encounter any issues with API keys, ensure they are correctly set in the `.env` file.
- For CORS issues, check that the server is properly configured to accept requests from the client's origin.
- Check Docker logs for any error messages:
  ```
  docker-compose logs python-server
  ```