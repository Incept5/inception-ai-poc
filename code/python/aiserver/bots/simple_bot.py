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

class SimpleBot(LangchainBotInterface):
    def __init__(self):
        super().__init__()
        self.tools = []  # SimpleBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "simple-bot"

    @property
    def description(self) -> str:
        return "Simple Bot - Basic conversation with optional RAG capabilities"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are a helpful AI assistant")

            prompt = """
            As an AI assistant, please provide a helpful and informative response to the user's query.
            Follow these guidelines:
            1. Be clear and specific in your answer
            2. If you're unsure about something, it's okay to admit it
            3. Break down complex information into manageable steps
            4. Use examples where appropriate
            5. Cite sources or provide reasoning for your answers when possible
            6. If relevant information is available from the retriever, incorporate it into your response
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            if self.retriever:
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm_wrapper.llm,
                    retriever=self.retriever,
                    memory=memory
                )
                result = qa_chain({"question": messages[-1].content})
                answer = result['answer']
            else:
                answer = self.llm_wrapper.invoke(messages).content

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