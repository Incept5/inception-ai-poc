# langgraph_tutorial_api.py

import os
import sys
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from flask import Flask, request, jsonify
from flask_cors import CORS

# Function to print debug information
def debug_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Print all environment variables (be cautious with this in production)
debug_print("Environment variables:")
for key, value in os.environ.items():
    debug_print(f"{key}: {value}")

# Get environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY")
ANTHROPIC_DEFAULT_MODEL = os.environ.get("ANTHROPIC_DEFAULT_MODEL", "claude-3-haiku-20240307")
LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.environ.get("LANGCHAIN_PROJECT", "LangGraph Tutorial")

# Check if required environment variables are set
if not ANTHROPIC_API_KEY or not LANGSMITH_API_KEY:
    raise ValueError("Required API keys not found. Please check your .env file.")

debug_print(f"ANTHROPIC_API_KEY: {'*' * len(ANTHROPIC_API_KEY)}")  # Print asterisks for security
debug_print(f"LANGSMITH_API_KEY: {'*' * len(LANGSMITH_API_KEY)}")  # Print asterisks for security
debug_print(f"ANTHROPIC_DEFAULT_MODEL: {ANTHROPIC_DEFAULT_MODEL}")
debug_print(f"LANGCHAIN_TRACING_V2: {LANGCHAIN_TRACING_V2}")
debug_print(f"LANGCHAIN_PROJECT: {LANGCHAIN_PROJECT}")

# Define the State type
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph builder
graph_builder = StateGraph(State)

# Set up the LLM and chatbot function
llm = ChatAnthropic(model=ANTHROPIC_DEFAULT_MODEL)

def chatbot(state: State):
    debug_print(f"Chatbot input state: {state}")
    result = {"messages": [llm.invoke(state["messages"])]}
    debug_print(f"Chatbot output: {result}")
    return result

# Add the chatbot node to the graph
graph_builder.add_node("chatbot", chatbot)

# Set entry and finish points
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

# Compile the graph
graph = graph_builder.compile()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

debug_print("Flask app initialized with CORS support")

@app.route('/chat', methods=['POST'])
def chat():
    debug_print("Received POST request to /chat")
    data = request.json
    debug_print(f"Request data: {data}")
    user_input = data.get('message')

    if not user_input:
        debug_print("Error: No message provided")
        return jsonify({"error": "No message provided"}), 400

    debug_print(f"User input: {user_input}")

    response = None
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            response = value["messages"][-1].content

    debug_print(f"Response: {response}")

    return jsonify({"response": response})

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=5010, debug=True)