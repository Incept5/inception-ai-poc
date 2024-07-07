import os
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
import chromadb

class RetrieverManager:
    def __init__(self):
        self.embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "openai")
        self.embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.embeddings = self._get_embeddings()
        self.persist_directory = "data/chroma_db"
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def _get_embeddings(self):
        if self.embedding_provider == "openai":
            return OpenAIEmbeddings(model=self.embedding_model)
        elif self.embedding_provider == "huggingface":
            return HuggingFaceEmbeddings(model_name=self.embedding_model)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")

    def process_pdfs(self, name: str):
        pdf_directory = f"data/imported/{name}"
        if not os.path.exists(pdf_directory):
            print(f"Directory {pdf_directory} does not exist.")
            return

        collection_name = f"{name}_collection"
        if collection_name in self.client.list_collections():
            print(f"Collection {collection_name} already exists. Skipping processing.")
            return

        documents = []
        for filename in os.listdir(pdf_directory):
            if filename.endswith(".pdf"):
                file_path = os.path.join(pdf_directory, filename)
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=collection_name,
        )
        vectorstore.persist()
        print(f"Processed and persisted {len(splits)} chunks for {name}")

    def get_retriever(self, name: str):
        collection_name = f"{name}_collection"
        if collection_name not in self.client.list_collections():
            print(f"Collection {collection_name} does not exist.")
            return None

        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=collection_name,
        )
        return vectorstore.as_retriever()

retriever_manager = RetrieverManager()