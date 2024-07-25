from typing import List, TypedDict, Annotated, Optional, Literal
from mylangchain.async_langchain_bot_interface import AsyncLangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool
import functools
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str

class SupervisorAgentBot(AsyncLangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None):
        super().__init__(retriever_name, default_llm_provider="openai", default_llm_model="gpt-4-turbo")
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "supervisor-agent-bot"

    @property
    def description(self) -> str:
        return "Supervisor Agent Bot - Multi-agent collaboration with a supervisor using LangGraph"

    def get_tools(self) -> List:
        return [self.tavily_tool, self.python_repl]

    def initialize(self):
        self.tavily_tool = TavilySearchResults(max_results=5)
        self.python_repl = PythonREPLTool()

    def create_agent(self, tools, system_message: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI assistant with a specific role in a team. "
                    "Use the provided tools to progress towards answering the question. "
                    "You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        tool_names = ", ".join([tool.name for tool in tools])
        prompt = prompt.partial(tool_names=tool_names)
        return prompt | self.llm_wrapper.llm.bind_tools(tools)

    def create_orchestrator(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI orchestrator overseeing a team of AI assistants. "
                    "Your role is to coordinate their efforts, provide guidance, "
                    "and ensure the team is making progress towards the goal. "
                    "Analyze the work done so far and decide which agent should act next, "
                    "or if the task is complete. "
                    "Available agents are: Researcher and chart_generator. "
                    "Respond with the name of the agent that should act next, "
                    "or 'FINAL' if the task is complete."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        return prompt | self.llm_wrapper.llm

    def agent_node(self, state, agent, name):
        debug_print(f"[DEBUG] Agent Node: {name}")
        result = agent.invoke(state)
        if isinstance(result, ToolMessage):
            debug_print("[DEBUG] Result is a ToolMessage")
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        return {"messages": state["messages"] + [result], "sender": name}

    def orchestrator_node(self, state):
        debug_print("[DEBUG] Orchestrator Node")
        orchestrator = self.create_orchestrator()
        result = orchestrator.invoke(state)
        decision = result.content.strip().lower()
        return {"messages": state["messages"], "sender": "Orchestrator", "decision": decision}

    def router(self, state) -> Literal["Researcher", "chart_generator", "__end__"]:
        decision = state.get("decision", "").lower()
        
        if decision == "researcher":
            return "Researcher"
        elif decision == "chart_generator":
            return "chart_generator"
        elif decision == "final":
            return "__end__"
        else:
            # Default to Researcher if decision is unclear
            return "Researcher"

    def create_graph(self) -> StateGraph:
        research_agent = self.create_agent(
            [self.tavily_tool],
            system_message="You are the Researcher. Provide accurate data for the chart generator to use."
        )
        research_node = functools.partial(self.agent_node, agent=research_agent, name="Researcher")

        chart_agent = self.create_agent(
            [self.python_repl],
            system_message="You are the Chart Generator. Create and save charts based on the data provided by the Researcher."
        )
        chart_node = functools.partial(self.agent_node, agent=chart_agent, name="chart_generator")

        workflow = StateGraph(AgentState)

        workflow.add_node("Researcher", research_node)
        workflow.add_node("chart_generator", chart_node)
        workflow.add_node("Orchestrator", self.orchestrator_node)

        workflow.add_conditional_edges(
            "Orchestrator",
            self.router,
            {
                "Researcher": "Researcher",
                "chart_generator": "chart_generator",
                "__end__": END,
            },
        )
        workflow.add_edge("Researcher", "Orchestrator")
        workflow.add_edge("chart_generator", "Orchestrator")

        workflow.add_edge(START, "Orchestrator")

        mycheckpointer = self.get_checkpointer()
        return workflow.compile(checkpointer=mycheckpointer)
