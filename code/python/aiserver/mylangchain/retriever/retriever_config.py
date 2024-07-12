import os
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from utils.debug_utils import debug_print

class RetrieverConfig:
    def __init__(self):
        self.default_embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "openai")
        self.default_embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.persist_directory = "/data/embeddings/__chromadb"
        self.embeddings_cache = {}

        # Set TOKENIZERS_PARALLELISM environment variable
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

    def get_embeddings(self, provider=None, model=None):
        provider = provider or self.default_embedding_provider
        model = model or self.default_embedding_model
        
        cache_key = f"{provider}:{model}"
        
        if cache_key not in self.embeddings_cache:
            debug_print(f"Initializing embeddings for provider: {provider}, model: {model}")
            if provider == "openai":
                embeddings = OpenAIEmbeddings(model=model)
            elif provider == "huggingface":
                embeddings = HuggingFaceEmbeddings(model_name=model)
            else:
                raise ValueError(f"Unsupported embedding provider: {provider}")
            
            self.embeddings_cache[cache_key] = embeddings
        
        return self.embeddings_cache[cache_key]

retriever_config = RetrieverConfig()