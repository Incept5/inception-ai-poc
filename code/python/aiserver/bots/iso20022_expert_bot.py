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

class ISO20022ExpertBot(LangchainBotInterface):
    def __init__(self):
        super().__init__(retriever_name="iso20022")  # Use the iso20022 retriever
        self.tools = []  # ISO20022ExpertBot doesn't use any tools
        self.initialize()

    @property
    def bot_type(self) -> str:
        return "iso20022-expert-bot"

    @property
    def description(self) -> str:
        return "ISO20022 Expert Bot - Answers questions and provides expertise on all aspects of ISO20022 standards"

    def get_tools(self) -> List:
        return self.tools

    def create_chatbot(self):
        def chatbot(state: State):
            debug_print(f"Chatbot input state: {state}")
            messages = state["messages"]
            system_message = SystemMessage(content="You are an AI assistant specialized in ISO20022 standards. Your role is to provide expert knowledge and answer questions related to all aspects of ISO20022.")

            prompt = """
            As an ISO20022 expert AI assistant, please provide informative and accurate responses based on the retrieved information about ISO20022 standards.
            Follow these guidelines:
            1. Use the provided information to answer questions accurately about ISO20022
            2. If you're unsure about something or it's not in the retrieved information, it's okay to admit it
            3. Provide specific details about ISO20022 when relevant, including message types, XML schemas, and implementation guidelines
            4. Be professional and respectful in your responses
            5. If asked about topics not directly related to ISO20022, politely redirect the conversation to ISO20022-related subjects
            6. Explain complex ISO20022 concepts in a clear and understandable manner
            7. When appropriate, mention the benefits and challenges of implementing ISO20022 standards
            """

            prompt_message = HumanMessage(content=prompt)
            messages = [system_message, prompt_message] + messages

            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm_wrapper.llm,  # Use the underlying LLM, not the wrapper
                retriever=self.retriever,
                return_source_documents=True
            )

            # Use the invoke method instead of calling the chain directly
            result = qa_chain.invoke({"question": messages[-1].content, "chat_history": messages[:-1]})
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