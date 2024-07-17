import os
from typing import List, TypedDict, Annotated, Optional
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from utils.file_tree import file_tree
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.tools import Tool
from prompts.system_prompts import file_saving_prompt


class State(TypedDict):
    messages: Annotated[List, add_messages]


class BaseSystemImproverBot(LangchainBotInterface):
    def __init__(self, system_src: str = '/system_src'):
        super().__init__()
        self.system_src = system_src
        self.tools = [self._create_file_content_tool()]
        self.initialize()

    def _create_file_content_tool(self):
        return Tool(
            name="file_content",
            func=self.file_content,
            description="Get the content of a file, handling paths that may or may not start with the system source directory."
        )

    @property
    def bot_type(self) -> str:
        return "base-system-improver-bot"

    @property
    def description(self) -> str:
        return "Base System Improver Bot - Answer questions about the system and suggest improvements"

    def get_tools(self) -> List:
        return self.tools

    def file_content(self, file_path: Optional[str] = None) -> str:
        """Get the content of a file, handling paths that may or may not start with the system source directory."""
        debug_print(f"file_content tool called with file_path: {file_path}")

        if file_path is None:
            debug_print("Error: No file path provided.")
            return "Error: No file path provided."

        debug_print(f"System source directory: {self.system_src}")

        if file_path.startswith(self.system_src):
            full_path = file_path
        else:
            full_path = os.path.join(self.system_src, file_path)

        debug_print(f"Full path: {full_path}")

        if os.path.exists(full_path):
            debug_print(f"File exists: {full_path}")
            if os.path.isfile(full_path):
                debug_print(f"Is a file: {full_path}")
                try:
                    with open(full_path, 'r') as file:
                        content = file.read()
                    debug_print(f"File content read successfully: {full_path}")
                    return content
                except Exception as e:
                    debug_print(f"Error reading file: {full_path}. Error: {str(e)}")
                    return f"Error reading file: {file_path}. Error: {str(e)}"
            else:
                debug_print(f"Path is not a file: {full_path}")
                return f"Error: {file_path} is not a file."
        else:
            debug_print(f"File not found: {full_path}")
            return f"Error: File {file_path} not found."

    def create_chatbot(self):
        def chatbot(state: State):
            file_structure = file_tree(self.system_src)
            debug_print(f"File structure: {file_structure}")

            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content=file_saving_prompt())

            # Check for hints.md file
            debug_print("Attempting to read hints.md")
            hints_content = self.file_content("hints.md")
            hints_section = ""
            if not hints_content.startswith("Error:"):
                hints_section = f"""
                Here are some hints about the system:
                {hints_content}
                """
            else:
                debug_print(f"Error reading hints.md: {hints_content}")

            prompt = f"""
            As an AI assistant, you are tasked with analyzing and suggesting improvements for a software system.
            Follow these guidelines:
            1. Review the system structure tree below and answer questions about the system and suggest improvements where appropriate.
            2. When making changes to the system:
               a. First, fetch all the files you think you might need using the file_content tool.
               b. Make a clear plan with multiple steps.
               c. Iterate through the plan, generating one file at a time.
            3. Use the file_content tool to retrieve the contents of specific files when needed rather than guessing at what they contain.
               When making edits to previously referenced files, always keep the name/path the same.
            4. When choosing a file path for generated artifacts, consider the system structure and choose a logical location.
            5. When a specific file name is mentioned, look for it in the system structure below and use the file_content tool to get the content of that file.
            6. Consider the following when suggesting improvements:
               a. Code organization and structure
               b. Adherence to best practices and design patterns
               c. Performance optimizations
               d. Security considerations
               e. Scalability and maintainability
               f. Documentation and comments
            7. Provide clear explanations for your suggestions and recommendations.
            8. If you need to create new files or modify existing ones, clearly indicate the file path and content.
            9. When generating new code or modifying existing code, always look at similar or nearby files in the source tree for guidance on:
               a. Code style and formatting
               b. Logging practices
               c. Error handling
               d. Import statements and module organization
               e. Commenting style and docstring format
               f. Naming conventions for variables, functions, and classes
            10. To find similar files:
                a. Examine the file structure provided below.
                b. Identify files in the same directory or nearby directories with similar purposes or file extensions.
                c. Use the file_content tool to retrieve the contents of these similar files for reference.
            11. Ensure that new code generation and modifications align with the existing codebase's style and best practices.

            The system structure is as follows:
            {file_structure}

            {hints_section}

            IMPORTANT: Remember to ask for specific file contents using the file_content tool when needed.
            Context: You are improving and analyzing a complex software system. Your goal is to provide comprehensive and well-thought-out suggestions for improvement.
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages
            result = {"messages": [self.llm_wrapper.invoke(messages)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        tool_node = ToolNode(tools=self.tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)