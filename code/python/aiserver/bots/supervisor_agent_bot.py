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
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_openai import ChatOpenAI
import functools
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str


class SupervisorAgentBot(AsyncLangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None):
        super().__init__(retriever_name, default_llm_provider="openai", default_llm_model="gpt-4-turbo")
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "supervisor-agent-bot"

    @property
    def description(self) -> str:
        return "Supervisor Agent Bot - Multi-agent collaboration using LangGraph with a supervisor"

    def get_tools(self) -> List:
        return [self.tavily_tool, self.python_repl]

    def initialize(self):
        self.tavily_tool = TavilySearchResults(max_results=5)
        self.python_repl = PythonREPLTool()

    def create_agent(self, tools, system_message: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(self.llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools)

    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        return {"messages": [HumanMessage(content=result["output"], name=name)]}

    def create_supervisor(self):
        members = ["Researcher", "Coder"]
        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )
        options = ["FINISH"] + members
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    }
                },
                "required": ["next"],
            },
        }
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(members))

        return (
                prompt
                | self.llm.bind_functions(functions=[function_def], function_call="route")
                | JsonOutputFunctionsParser()
        )

    def create_graph(self) -> StateGraph:
        research_agent = self.create_agent(
            [self.tavily_tool],
            "You are a web researcher. Use the provided tools to find accurate information."
        )
        research_node = functools.partial(self.agent_node, agent=research_agent, name="Researcher")

        code_agent = self.create_agent(
            [self.python_repl],
            "You are a coder. Generate and run Python code to analyze data and create charts using matplotlib."
        )
        code_node = functools.partial(self.agent_node, agent=code_agent, name="Coder")

        supervisor_chain = self.create_supervisor()

        workflow = StateGraph(AgentState)
        workflow.add_node("Researcher", research_node)
        workflow.add_node("Coder", code_node)
        workflow.add_node("supervisor", supervisor_chain)

        members = ["Researcher", "Coder"]
        for member in members:
            workflow.add_edge(member, "supervisor")

        conditional_map = {k: k for k in members}
        conditional_map["FINISH"] = END
        workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
        workflow.add_edge(START, "supervisor")

        return workflow.compile()

    async def process_input(self, input_text: str, thread_id: str) -> str:
        graph = self.create_graph()

        # Initialize the state with the input message
        initial_state = {
            "messages": [HumanMessage(content=input_text)],
            "next": "supervisor"
        }

        # Run the graph
        final_output = None
        for output in graph.stream(initial_state):
            final_output = output
            if output["next"] == "FINISH":
                break

        # Check if we have a valid final output
        if final_output and final_output.get("messages"):
            return final_output["messages"][-1].content
        else:
            return "An error occurred while processing your request."
