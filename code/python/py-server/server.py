# langgraph_tutorial_api.py

import os
import sys
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
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
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
ANTHROPIC_DEFAULT_MODEL = os.environ.get("ANTHROPIC_DEFAULT_MODEL", "claude-3-haiku-20240307")
LANGCHAIN_TRACING_V2 = os.environ.get("LANGCHAIN_TRACING_V2", "true")
LANGCHAIN_PROJECT = os.environ.get("LANGCHAIN_PROJECT", "LangGraph Tutorial")

# Check if required environment variables are set
if not all([ANTHROPIC_API_KEY, LANGSMITH_API_KEY, TAVILY_API_KEY]):
    raise ValueError("Required API keys not found. Please check your .env file.")

debug_print(f"ANTHROPIC_API_KEY: {'*' * len(ANTHROPIC_API_KEY)}")  # Print asterisks for security
debug_print(f"LANGSMITH_API_KEY: {'*' * len(LANGSMITH_API_KEY)}")  # Print asterisks for security
debug_print(f"TAVILY_API_KEY: {'*' * len(TAVILY_API_KEY)}")  # Print asterisks for security
debug_print(f"ANTHROPIC_DEFAULT_MODEL: {ANTHROPIC_DEFAULT_MODEL}")
debug_print(f"LANGCHAIN_TRACING_V2: {LANGCHAIN_TRACING_V2}")
debug_print(f"LANGCHAIN_PROJECT: {LANGCHAIN_PROJECT}")

# Define the State type
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create the graph builder
graph_builder = StateGraph(State)

# Set up the search tool
tool = TavilySearchResults(max_results=2)
tools = [tool]

# Set up the LLM and chatbot function
llm = ChatAnthropic(model=ANTHROPIC_DEFAULT_MODEL)
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    debug_print(f"Chatbot input state: {state}")
    result = {"messages": [llm_with_tools.invoke(state["messages"])]}
    debug_print(f"Chatbot output: {result}")
    return result

# Add the chatbot node to the graph
graph_builder.add_node("chatbot", chatbot)

# Add the tool node
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# Add conditional edges
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# Add edge from tools back to chatbot
graph_builder.add_edge("tools", "chatbot")

# Set entry point
graph_builder.set_entry_point("chatbot")

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

    final_response = None
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            if isinstance(value["messages"][-1], BaseMessage):
                final_response = value["messages"][-1].content

    debug_print(f"Final response: {final_response}")
    return jsonify({"response": final_response})

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=5010, debug=True)