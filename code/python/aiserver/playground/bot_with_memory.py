import os
import sys
from dotenv import load_dotenv
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Load environment variables from .env file
load_dotenv("./../../../../.env")

def debug_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-haiku-20240307")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

def tools_condition(state: State) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    if isinstance(last_message, BaseMessage):
        content = last_message.content
    else:
        content = last_message[1]
    if "use tool" in content.lower():
        return "tools"
    else:
        return END

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

# Use in-memory SQLite database for the checkpointer
memory = SqliteSaver.from_conn_string(":memory:")
graph = graph_builder.compile(checkpointer=memory)

def main():
    print("Bot: Hello! I'm your AI assistant. How can I help you today?")
    config = {"configurable": {"thread_id": "1"}}

    while True:
        snapshot = graph.get_state(config)
        debug_print(f"Snapshot: {snapshot}")

        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Bot: Goodbye! Have a great day.")
            break

        try:
            events = graph.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config,
                stream_mode="values"
            )

            for event in events:
                ai_message = event["messages"][-1]
                print("Bot:", ai_message.content)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Bot: I'm sorry, but I encountered an error. Let's try again.")

if __name__ == "__main__":
    main()