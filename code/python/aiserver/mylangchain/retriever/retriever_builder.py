from langchain_community.vectorstores import Chroma
from utils.debug_utils import debug_print
from .retriever_config import retriever_config
from .vector_db_loader import vector_db_loader

class RetrieverBuilder:
    @staticmethod
    def get_retriever(name: str):
        debug_print(f"Getting retriever for: {name}")
        try:
            vector_db_loader.process_documents(name)  # Ensure the collection is up-to-date
            collection_name = f"{name}_collection"
            if not vector_db_loader.verify_collection_exists(name):
                debug_print(f"Error: Collection {collection_name} does not exist.")
                return None

            debug_print(f"Creating Chroma vectorstore for {collection_name}")
            vectorstore = Chroma(
                client=vector_db_loader.client,
                embedding_function=retriever_config.get_embeddings(),
                collection_name=collection_name,
            )
            debug_print(f"Retriever created for {name}")
            return vectorstore.as_retriever()
        except Exception as e:
            debug_print(f"Error in get_retriever: {str(e)}")
            return None

retriever_builder = RetrieverBuilder()