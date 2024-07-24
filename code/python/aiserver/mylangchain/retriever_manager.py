import os
from typing import Optional, List
from utils.debug_utils import debug_print
from .retriever.retriever_config import retriever_config
from .retriever.vector_db_loader import vector_db_loader
from .retriever.retriever_builder import retriever_builder

class RetrieverManager:
    def __init__(self):
        self.config = retriever_config
        self.loader = vector_db_loader
        self.builder = retriever_builder

    async def check_imports(self, names: Optional[List[str]] = None):
        debug_print("Checking imports and initializing RetrieverManager")
        # Initialize embeddings by calling get_embeddings() instead of initialize_embeddings()
        self.config.get_embeddings()
        await self.loader.initialize_client()
        
        if names is None:
            configured_importers = os.getenv("CONFIGURED_IMPORTERS", "")
            names = [name.strip() for name in configured_importers.split(",")] if configured_importers else []
        
        debug_print(f"Processing importers: {names}")
        for name in names:
            await self.loader.process_documents(name)

    def get_retriever(self, name: str):
        return self.builder.get_retriever(name)

retriever_manager = RetrieverManager()
debug_print("RetrieverManager instance created")