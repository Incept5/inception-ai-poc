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

class SimpleRetrieverBot(LangchainBotInterface):
    def __init__(self):
        super().__init__(retriever_name="uktax")
        self.tools = []  # SimpleRetrieverBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "simple-retriever-bot"

    @property
    def description(self) -> str:
        return "Simple Retriever Bot - Answers questions using a basic Retrieval-Augmented Generation approach"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm_wrapper.llm,
            retriever=self.retriever,
            return_source_documents=True
        )

        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an AI assistant that answers questions based on the provided information.")

            prompt = """
            As an AI assistant, please provide informative responses based on the retrieved information.
            Follow these guidelines:
            1. Use the provided information to answer questions accurately
            2. If you're unsure about something or it's not in the retrieved information, it's okay to admit it
            3. Provide specific details when relevant
            4. Be professional and respectful in your responses
            5. If asked about topics not covered in the retrieved information, politely state that you don't have that information
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            # Debug print: Show the question being asked to the retriever
            debug_print(f"Question being asked to the retriever: {messages[-1].content}")

            # Use the invoke method instead of __call__
            result = qa_chain.invoke({"question": messages[-1].content, "chat_history": messages[:-1]})
            answer = result['answer']
            source_docs = result['source_documents']

            # Debug print: Show the retrieved documents
            debug_print(f"Retrieved documents:")
            for i, doc in enumerate(source_docs, 1):
                debug_print(f"Document {i}:")
                debug_print(f"  Content: {doc.page_content[:100]}...")  # Print first 100 characters of content
                debug_print(f"  Metadata: {doc.metadata}")

            # Append source information to the answer
            if source_docs:
                answer += "\n\nSources:"
                for i, doc in enumerate(source_docs, 1):
                    answer += f"\n{i}. {doc.metadata.get('source', 'Unknown source')}"

            # Debug print: Show the final answer
            debug_print(f"Final answer: {answer}")

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