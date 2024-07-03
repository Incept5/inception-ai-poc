# LangGraph Chatbot Project

This project implements a chatbot using [LangGraph](https://langchain-ai.github.io/langgraph/), Flask, and Docker. It consists of a Python backend server and a simple HTML client.

This project is a starting point for building a chatbot that can interact with LangGraph's conversational AI models. The server is set up to handle incoming messages from the client, send them to LangGraph's API, and return the responses to the client.

We are working through the tutoral here but making it work in a client/server model:

https://langchain-ai.github.io/langgraph/tutorials/introduction/

# Features

The UI allows you to change the following:

* Which bot you are talking to
  * You can add new bots under /code/python/py-server/bots/
  * Make sure you also add that bot to /code/python/py-server/bots/configured_bots.py
* Which LLM Provider you are using
  * Local or remote Ollama (via OLLAMA_BASE_URL in .env)
  * Anthropic Claude
  * Open AI
* Which LLM model you are using
  * Will query Ollama for the list of installed models

# Example Bots

* Simple Bot - [code/python/py-server/bots/simple_bot.py](code/python/py-server/bots/simple_bot.py)
  * Simple Langgraph bot with no tools 
* Web Search Bot - [code/python/py-server/bots/web_search_bot.py](code/python/py-server/bots/web_search_bot.py)
  * Langgraph bot with a web search tool
* Ollama Bot - [code/python/py-server/bots/ollama_bot.py](code/python/py-server/bots/ollama_bot.py)
   * This bot does not use langchain at all

## Project Structure

```
.
├── .env (ignored)
├── .example.env
├── README.md
├── docker
│   ├── docker-compose.yml
│   └── Dockerfile.python-server
└── code
    ├── webapp
    │   └── simple-client.html
    └── python
        └── py-server (this is the AI Codebase)
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

   This command will build the Python server image and start the container. The server will be accessible at `http://localhost:5010`.

3. To stop the containers, use:
   ```
   docker-compose down
   ```

## Using the Chatbot

1. Open the `code/webapp/simple-client.html` file in a web browser.

2. You should see a simple interface where you can type messages and receive responses from the chatbot.

3. The client will communicate with the server running at `http://localhost:5010`.

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