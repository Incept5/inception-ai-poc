import os
from typing import List, TypedDict, Annotated, Optional
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase

class State(TypedDict):
    messages: Annotated[List, add_messages]

class SimpleDBBot(LangchainBotInterface):
    def __init__(self, retriever_name: Optional[str] = None, db_url: str = os.environ.get("DB_READER_DB_URI")):
        super().__init__(retriever_name)
        self.db_url = db_url
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "simple-db-bot"

    @property
    def description(self) -> str:
        return "Simple DB Bot - SQL database interaction"

    def get_tools(self) -> List:
        return []  # Tools are handled by the SQL agent

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant that can interact with a SQL database.")

            prompt = """
            As an AI assistant with SQL database capabilities, please provide helpful and informative responses to the user's queries.
            Follow these guidelines:
            1. Use the SQL agent to query the database when necessary
            2. Be clear and specific in your answers
            3. If you're unsure about something, it's okay to admit it
            4. Break down complex information into manageable steps
            5. Use examples where appropriate
            6. Cite sources or provide reasoning for your answers when possible
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            llm = self.llm_wrapper.llm
            db = SQLDatabase.from_uri(self.db_url)
            agent_executor = create_sql_agent(llm, db=db, agent_type="tool-calling", verbose=True)

            # Use the SQL agent to process the user's query
            result = agent_executor.invoke({"input": messages[-1].content})
            answer = result["output"]

            result = {"messages": [HumanMessage(content=answer)]}
            debug_print(f"Chatbot output: {result}")
            return result

        return chatbot

    def create_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", self.create_chatbot())
        graph_builder.set_entry_point("chatbot")
        mycheckpointer = self.get_checkpointer()
        return graph_builder.compile(checkpointer=mycheckpointer)