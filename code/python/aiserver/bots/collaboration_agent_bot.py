from typing import List, TypedDict, Annotated, Optional, Literal
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
import functools
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str

class CollaborationAgentBot(LangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None):
        super().__init__(retriever_name,default_llm_provider="openai", default_llm_model="gpt-4-turbo-preview")
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "collaboration-agent-bot"

    @property
    def description(self) -> str:
        return "Collaboration Agent Bot - Multi-agent collaboration using LangGraph"

    def get_tools(self) -> List:
        return [self.tavily_tool, self.python_repl]

    def initialize(self):
        self.tavily_tool = TavilySearchResults(max_results=5)
        self.repl = PythonREPL()

        @tool
        def python_repl(code: str):
            """Use this to execute python code. If you want to see the output of a value,
            you should print it out with `print(...)`. This is visible to the user."""
            debug_print(f"[DEBUG] Executing Python code:\n{code}")
            try:
                result = self.repl.run(code)
                debug_print(f"[DEBUG] Execution result:\n{result}")
            except BaseException as e:
                error_message = f"Failed to execute. Error: {repr(e)}"
                debug_print(f"[DEBUG] Execution error: {error_message}")
                return error_message
            result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
            debug_print(f"[DEBUG] Formatted result:\n{result_str}")
            return result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."

        self.python_repl = python_repl

    def create_agent(self, tools, system_message: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK, another assistant with different tools "
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any of the other assistants have the final answer or deliverable,"
                    " prefix your response with FINAL ANSWER so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        return prompt | self.llm_wrapper.llm.bind_tools(tools)

    def agent_node(self, state, agent, name):
        debug_print(f"[DEBUG] Agent Node: {name}")
        debug_print(f"[DEBUG] Input State: {state}")
        debug_print(f"[DEBUG] Agent: {agent}")

        result = agent.invoke(state)
        debug_print(f"[DEBUG] Agent Result: {result}")

        if isinstance(result, ToolMessage):
            debug_print("[DEBUG] Result is a ToolMessage")
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
            debug_print(f"[DEBUG] Result converted to AIMessage: {result}")

        output_state = {
            "messages": [result],
            "sender": name,
        }
        debug_print(f"[DEBUG] Output State: {output_state}")
        return output_state

    def router(self, state) -> Literal["call_tool", "__end__", "continue"]:
        messages = state["messages"]
        sender = state["sender"]
        last_message = messages[-1]
        
        debug_print(f"Router: Current messages: {messages}")
        debug_print(f"Router: Last message: {last_message}")
        
        if last_message.tool_calls:
            debug_print("Router: Routing to 'call_tool' due to tool calls in the last message")
            return "call_tool"
        if sender is not "Researcher" and "FINAL ANSWER" in last_message.content:
            debug_print("Router: Routing to '__end__' due to 'FINAL ANSWER' in the last message")
            return "__end__"
        
        debug_print("Router: Routing to 'continue' as no special conditions were met")
        return "continue"

    def create_graph(self) -> StateGraph:
        research_agent = self.create_agent(
            [self.tavily_tool],
            system_message="You should provide accurate data for the chart_generator to use.",
        )
        research_node = functools.partial(self.agent_node, agent=research_agent, name="Researcher")

        chart_agent = self.create_agent(
            [self.python_repl],
            system_message="Any charts you display will be visible by the user. When generating a chart use the thread_id from the context to save the chart image to /mnt/__threads/{thread_id}/{chart_name}.png. Also remember to create the dir if necessary before saving the file.",
        )
        chart_node = functools.partial(self.agent_node, agent=chart_agent, name="chart_generator")

        tool_node = ToolNode(self.get_tools())

        workflow = StateGraph(AgentState)

        workflow.add_node("Researcher", research_node)
        workflow.add_node("chart_generator", chart_node)
        workflow.add_node("call_tool", tool_node)

        workflow.add_conditional_edges(
            "Researcher",
            self.router,
            {"continue": "chart_generator", "call_tool": "call_tool", "__end__": END},
        )
        workflow.add_conditional_edges(
            "chart_generator",
            self.router,
            {"continue": "Researcher", "call_tool": "call_tool", "__end__": END},
        )

        workflow.add_conditional_edges(
            "call_tool",
            lambda x: x["sender"],
            {
                "Researcher": "Researcher",
                "chart_generator": "chart_generator",
            },
        )
        workflow.add_edge(START, "Researcher")

        mycheckpointer = self.get_checkpointer()
        return workflow.compile(checkpointer=mycheckpointer)

   