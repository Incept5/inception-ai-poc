from typing import List, TypedDict, Annotated
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

class State(TypedDict):
    messages: Annotated[List, add_messages]

class ISO20022Bot(LangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = []  # ISO20022Bot doesn't use any tools
        self.initialize(retriever_name="iso20022")

    @property
    def bot_type(self) -> str:
        return "iso20022-bot"

    @property
    def description(self) -> str:
        return "ISO 20022 Bot - Specialized in answering questions about ISO 20022 standards"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an AI assistant specialized in ISO 20022 standards.")

            prompt = """
            As an AI assistant specializing in ISO 20022 standards, please provide accurate and helpful responses to user queries.
            Follow these guidelines:
            1. Focus on ISO 20022 standards, financial messaging, and related topics
            2. Use technical terminology accurately and explain it when necessary
            3. Refer to specific ISO 20022 message types, elements, and structures when relevant
            4. If you're unsure about something, admit it and suggest where the user might find more information
            5. Use examples from common financial scenarios to illustrate ISO 20022 concepts
            6. Incorporate relevant information from the ISO 20022 retriever into your responses
            7. Be prepared to explain the benefits and challenges of ISO 20022 adoption in the financial industry
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm_wrapper.llm,
                retriever=self.retriever,
                memory=memory
            )
            result = qa_chain({"question": messages[-1].content})
            answer = result['answer']

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