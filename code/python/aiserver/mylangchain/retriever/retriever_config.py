import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.debug_utils import debug_print

class RetrieverConfig:
    def __init__(self):
        self.embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "openai")
        self.embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.persist_directory = "/data/embeddings/__chromadb"
        self.embeddings = None

    def initialize_embeddings(self):
        debug_print(f"Initializing embeddings for provider: {self.embedding_provider}")
        if self.embedding_provider == "openai":
            self.embeddings = OpenAIEmbeddings(model=self.embedding_model)
        elif self.embedding_provider == "huggingface":
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")

    def get_embeddings(self):
        if self.embeddings is None:
            self.initialize_embeddings()
        return self.embeddings

retriever_config = RetrieverConfig()