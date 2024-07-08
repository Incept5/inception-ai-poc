from typing import List, TypedDict, Annotated, Optional
from mylangchain.langchain_bot_interface import LangchainBotInterface
from utils.debug_utils import debug_print
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain

class State(TypedDict):
    messages: Annotated[List, add_messages]

class AdamBot(LangchainBotInterface):
    def __init__(self):
        super().__init__(retriever_name="adam")
        self.tools = []  # AdamBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "adam-bot"

    @property
    def description(self) -> str:
        return "Adam Bot - Answers questions about Adam's work history using his CV"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an AI assistant that answers questions about Adam's work history based on his CV.")

            prompt = """
            As an AI assistant, please provide informative responses about Adam's work history based on his CV.
            Follow these guidelines:
            1. Use the provided CV information to answer questions accurately
            2. If you're unsure about something or it's not in the CV, it's okay to admit it
            3. Provide specific details from Adam's work experience when relevant
            4. Be professional and respectful when discussing Adam's career
            5. If asked about skills or experiences not mentioned in the CV, politely state that you don't have that information
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm_wrapper.llm,  # Use the underlying LLM, not the wrapper
                retriever=self.retriever,
                return_source_documents=True
            )

            result = qa_chain({"question": messages[-1].content, "chat_history": messages[:-1]})
            answer = result['answer']
            source_docs = result['source_documents']

            # Append source information to the answer
            if source_docs:
                answer += "\n\nSources:"
                for i, doc in enumerate(source_docs, 1):
                    answer += f"\n{i}. {doc.metadata.get('source', 'Unknown source')}"

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