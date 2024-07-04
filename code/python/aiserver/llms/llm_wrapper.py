
from langchain_core.language_models import BaseChatModel

class LLMWrapper:
    def __init__(self, llm: BaseChatModel, provider: str):
        self.llm = llm
        self.provider = provider

    def invoke(self, *args, **kwargs):
        return self.llm.invoke(*args, **kwargs)