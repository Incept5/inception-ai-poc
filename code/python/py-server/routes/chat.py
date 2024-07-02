from flask import Blueprint, request, jsonify
from typing import Annotated, Dict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, SystemMessage
from services.llm_manager import get_llm, get_system_message, LLMWrapper
from utils.debug_utils import debug_print

chat_blueprint = Blueprint('chat', __name__)

class State(TypedDict):
    messages: Annotated[list, add_messages]

tool = TavilySearchResults(max_results=2)
tools = [tool]

def create_chatbot(llm_wrapper: LLMWrapper):
    def chatbot(state: State):
        debug_print(f"Chatbot input state: {state}")
        messages = state["messages"]
        system_message = SystemMessage(content=get_system_message(llm_wrapper.provider))
        messages = [system_message] + messages
        result = {"messages": [llm_wrapper.invoke(messages)]}
        debug_print(f"Chatbot output: {result}")
        return result
    return chatbot

def create_graph(llm_wrapper: LLMWrapper):
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", create_chatbot(llm_wrapper))
    tool_node = ToolNode(tools=[tool])
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    return graph_builder.compile()

@chat_blueprint.route('/chat', methods=['POST'])
def chat():
    debug_print("Received POST request to /chat")
    data = request.json
    debug_print(f"Request data: {data}")
    user_input = data.get('message')
    llm_provider = data.get('llm_provider', 'anthropic')
    llm_model = data.get('llm_model')

    if not user_input:
        debug_print("Error: No message provided")
        return jsonify({"error": "No message provided"}), 400

    debug_print(f"User input: {user_input}")
    debug_print(f"LLM Provider: {llm_provider}")
    debug_print(f"LLM Model: {llm_model}")

    # Create the graph for the current LLM configuration
    llm_wrapper = get_llm(tools, llm_provider, llm_model)
    graph = create_graph(llm_wrapper)

    final_response = None
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            if isinstance(value["messages"][-1], BaseMessage):
                final_response = value["messages"][-1].content

    debug_print(f"Final response: {final_response}")
    return jsonify({"response": final_response})
