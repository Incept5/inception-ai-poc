from typing import List, TypedDict, Annotated, Optional, Literal, Dict
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
import graphviz
import os

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str
    task: Optional[str]
    subtasks: List[str]
    completed_subtasks: List[str]

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
                    "Use the provided tools to progress towards completing your assigned subtask. "
                    "You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
                ("human", "Your current subtask is: {subtask}"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        tool_names = ", ".join([tool.name for tool in tools])
        prompt = prompt.partial(tool_names=tool_names)
        return prompt | self.llm_wrapper.llm.bind_tools(tools)

    def create_supervisor(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI supervisor overseeing a team of AI assistants. "
                    "Your role is to break down the main task into subtasks, assign them to agents, "
                    "coordinate their efforts, provide guidance, and ensure the team is making progress. "
                    "Available agents are: Researcher and chart_generator. "
                    "Analyze the work done so far and decide which subtask should be worked on next, "
                    "or if the main task is complete. "
                    "Respond with a JSON object containing: "
                    "{'decision': 'continue' or 'final', 'agent': 'Researcher' or 'chart_generator', 'subtask': 'description of the subtask'}"
                ),
                MessagesPlaceholder(variable_name="messages"),
                ("human", "The main task is: {task}\nCompleted subtasks: {completed_subtasks}\nRemaining subtasks: {subtasks}"),
            ]
        )
        return prompt | self.llm_wrapper.llm

    def agent_node(self, state: Dict, agent, name: str) -> Dict:
        debug_print(f"[DEBUG] Agent Node: {name}")
        messages = state["messages"]
        subtask = state.get("current_subtask", "No specific subtask assigned")
        
        agent_input = {
            "messages": messages,
            "subtask": subtask
        }
        
        result = agent.invoke(agent_input)
        
        if isinstance(result, ToolMessage):
            debug_print("[DEBUG] Result is a ToolMessage")
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        
        return {
            "messages": messages + [result],
            "sender": name,
            "task": state["task"],
            "subtasks": state["subtasks"],
            "completed_subtasks": state["completed_subtasks"],
            "current_subtask": subtask
        }

    def supervisor_node(self, state: Dict) -> Dict:
        debug_print("[DEBUG] Supervisor Node")
        supervisor = self.create_supervisor()
        
        supervisor_input = {
            "messages": state["messages"],
            "task": state["task"],
            "completed_subtasks": ", ".join(state["completed_subtasks"]),
            "subtasks": ", ".join(state["subtasks"])
        }
        
        result = supervisor.invoke(supervisor_input)
        decision = self.parse_supervisor_decision(result.content)
        
        if decision["decision"] == "continue":
            state["subtasks"].append(decision["subtask"])
            state["current_subtask"] = decision["subtask"]
        elif decision["decision"] == "final":
            state["completed_subtasks"].extend(state["subtasks"])
            state["subtasks"] = []
            state["current_subtask"] = None
        
        return {
            "messages": state["messages"] + [AIMessage(content=result.content, name="Supervisor")],
            "sender": "Supervisor",
            "task": state["task"],
            "subtasks": state["subtasks"],
            "completed_subtasks": state["completed_subtasks"],
            "current_subtask": state.get("current_subtask"),
            "decision": decision
        }

    def parse_supervisor_decision(self, content: str) -> Dict:
        # This is a simple parser. In a real-world scenario, you might want to use a more robust JSON parser.
        import json
        try:
            decision = json.loads(content)
            return {
                "decision": decision.get("decision", "continue"),
                "agent": decision.get("agent", "Researcher"),
                "subtask": decision.get("subtask", "")
            }
        except json.JSONDecodeError:
            debug_print("[DEBUG] Error parsing supervisor decision. Defaulting to continue with Researcher.")
            return {
                "decision": "continue",
                "agent": "Researcher",
                "subtask": "Continue the research"
            }

    def router(self, state: Dict) -> Literal["Researcher", "chart_generator", "__end__"]:
        decision = state.get("decision", {})
        
        if decision.get("decision") == "final":
            return "__end__"
        elif decision.get("agent") == "chart_generator":
            return "chart_generator"
        else:
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
        workflow.add_node("Supervisor", self.supervisor_node)

        workflow.add_conditional_edges(
            "Supervisor",
            self.router,
            {
                "Researcher": "Researcher",
                "chart_generator": "chart_generator",
                "__end__": END,
            },
        )
        workflow.add_edge("Researcher", "Supervisor")
        workflow.add_edge("chart_generator", "Supervisor")

        workflow.set_entry_point("Supervisor")

        mycheckpointer = self.get_checkpointer()
        return workflow.compile(checkpointer=mycheckpointer)

    async def process_input(self, user_input: str, thread_id: str) -> str:
        workflow = self.create_graph()
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "sender": "Human",
            "task": user_input,
            "subtasks": [],
            "completed_subtasks": [],
            "current_subtask": None
        }
        
        for output in workflow.stream(initial_state):
            if output["type"] == "end":
                final_state = output["state"]
                final_output = self.format_final_output(final_state)
                
                # Generate and add the diagram
                diagram_path = self.create_diagram(thread_id)
                final_output += f"\n\nWorkflow diagram saved at: {diagram_path}"
                
                return final_output
        
        return "An error occurred while processing the input."

    def format_final_output(self, final_state: Dict) -> str:
        messages = final_state["messages"]
        completed_subtasks = final_state["completed_subtasks"]
        
        output = "Task completed. Here's a summary of the work done:\n\n"
        output += f"Main task: {final_state['task']}\n\n"
        output += "Completed subtasks:\n"
        for i, subtask in enumerate(completed_subtasks, 1):
            output += f"{i}. {subtask}\n"
        output += "\nFinal output from the agents:\n"
        output += messages[-1].content
        
        return output

    def create_diagram(self, thread_id: str) -> str:
        dot = graphviz.Digraph(comment='SupervisorAgentBot Workflow')
        dot.attr(rankdir='TB', size='8,8')

        # Add nodes
        dot.node('Supervisor', 'Supervisor')
        dot.node('Researcher', 'Researcher')
        dot.node('ChartGenerator', 'Chart Generator')
        dot.node('Human', 'Human')

        # Add edges
        dot.edge('Human', 'Supervisor', 'Input task')
        dot.edge('Supervisor', 'Researcher', 'Assign research subtask')
        dot.edge('Supervisor', 'ChartGenerator', 'Assign chart creation subtask')
        dot.edge('Researcher', 'Supervisor', 'Return research results')
        dot.edge('ChartGenerator', 'Supervisor', 'Return chart')
        dot.edge('Supervisor', 'Human', 'Final output')

        # Save the diagram
        save_dir = f'/mnt/__threads/{thread_id}'
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, 'supervisor_agent_workflow.png')
        dot.render(file_path, format='png', cleanup=True)

        return file_path
