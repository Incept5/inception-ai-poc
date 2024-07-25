from typing import List, TypedDict, Annotated, Optional, Literal
from mylangchain.async_langchain_bot_interface import AsyncLangchainBotInterface
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

# The agent doesn't work with Claude's model due to a Langchain/Anthropic issue
# So we are setting the default provider to OpenAI and the model to gpt-4-turbo

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    sender: str

class CollaborationAgentBot(AsyncLangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None):
        super().__init__(retriever_name,default_llm_provider="openai", default_llm_model="gpt-4-turbo")
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
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        tool_names = ", ".join([tool.name for tool in tools])
        debug_print(f"[DEBUG] Tool names: {tool_names}")
        prompt = prompt.partial(tool_names=tool_names)
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
        if "FINAL ANSWER" in last_message.content:
            debug_print("Router: Routing to '__end__' due to 'FINAL ANSWER' in the last message")
            return "__end__"
        
        debug_print("Router: Routing to 'continue' as no special conditions were met")
        return "continue"

    def create_graph(self) -> StateGraph:
        research_agent = self.create_agent(
            [self.tavily_tool],
            system_message="You should use the Tavily Search API to find relevant information to answer the question and format it in a structured way and then say 'chart_generator do your thing'"
        )
        research_node = functools.partial(self.agent_node, agent=research_agent, name="Researcher")

        chart_agent = self.create_agent(
            [self.python_repl],
            system_message="""
            Write Python code to generate a chart using the data provided by the Researcher.
            Then run the code to generate the chart and save it to disk. Do not wrap the code in JSON when calling the Python REPL tool.
            Follow these steps carefully:
            
            1. IMPORTANT: Use the thread_id from the context to construct the save path:
               save_dir = f'/mnt/__threads/{thread_id}'
            
            2. CRITICAL: Create the directory before generating the chart:
               - Import the 'os' module
               - Use os.makedirs(save_dir, exist_ok=True) to ensure the directory exists
            
            3. Generate the chart using matplotlib or another appropriate library
            
            4. Save the chart image to disk at: {save_dir}/{chart_name}.png
            
            5. Check the output for errors and make any necessary adjustments
            
            6. IMPORTANT: After generating and saving the report say "FINAL ANSWER" to end the conversation.
            
            7. IMPORTANT: Always respond with the full path of the saved chart image
            
            Example Python code that demonstrates these steps:
            
            import matplotlib.pyplot as plt
            import os
            
            # Step 1: Construct the save path using thread_id
            thread_id = '1721485325915'  # Replace with actual thread_id from context
            save_dir = f'/mnt/__threads/{thread_id}'
            
            # Step 2: Ensure the directory exists
            os.makedirs(save_dir, exist_ok=True)
            
            # Step 3: Generate the chart (example)
            # Use the data provided by the Researcher to create your chart
            plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
            plt.title('Example Chart')
            
            # Step 4: Save the chart
            chart_name = 'example_chart.png'
            file_path = os.path.join(save_dir, chart_name)
            plt.savefig(file_path)
            
            # Step 5: Check for errors (add error handling as needed)
            
            # Step 6: Respond with the full path
            print(f"Saved chart to: {file_path}")
            """,
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

   