from langchain_community.vectorstores import Chroma
from utils.debug_utils import debug_print
from .retriever_config import retriever_config
from .vector_db_loader import vector_db_loader
import json
import os

class RetrieverBuilder:
    @staticmethod
    def get_retriever(name: str):
        debug_print(f"Getting retriever for: {name}")
        try:
            # Ensure the collection is up-to-date
            vector_db_loader.process_documents(name)
            collection_name = f"{name}_collection"
            
            if not vector_db_loader.verify_collection_exists(name):
                debug_print(f"Error: Collection {collection_name} does not exist.")
                return None

            # Load the retriever info to get the embedding provider and model
            retriever_info_path = os.path.join("/data/imported", name, "retriever-info.json")
            with open(retriever_info_path, 'r') as f:
                retriever_info = json.load(f)

            embedding_provider = retriever_info.get('embedding_provider')
            embedding_model = retriever_info.get('embedding_model')

            debug_print(f"Using embedding provider: {embedding_provider}, model: {embedding_model}")

            # Get the correct embedding function based on the stored info
            embedding_function = retriever_config.get_embeddings(provider=embedding_provider, model=embedding_model)

            debug_print(f"Creating Chroma vectorstore for {collection_name}")
            vectorstore = Chroma(
                client=vector_db_loader.client,
                embedding_function=embedding_function,
                collection_name=collection_name,
            )
            debug_print(f"Retriever created for {name}")
            return vectorstore.as_retriever()
        except Exception as e:
            debug_print(f"Error in get_retriever: {str(e)}")
            return None

retriever_builder = RetrieverBuilder()