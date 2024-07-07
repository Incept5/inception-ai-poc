import os
import json
from typing import List, Dict
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, UnstructuredXMLLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb

class RetrieverManager:
    def __init__(self):
        self.embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "openai")
        self.embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.embeddings = self._get_embeddings()
        self.persist_directory = "/data/embeddings/__chromadb"
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def _get_embeddings(self):
        if self.embedding_provider == "openai":
            return OpenAIEmbeddings(model=self.embedding_model)
        elif self.embedding_provider == "huggingface":
            return HuggingFaceEmbeddings(model_name=self.embedding_model)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")

    def _load_document(self, file_path: str):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            return PyPDFLoader(file_path).load()
        elif file_extension == ".xml":
            return UnstructuredXMLLoader(file_path).load()
        elif file_extension == ".txt":
            return TextLoader(file_path).load()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def _get_retriever_info_path(self, name: str):
        return f"/data/imported/{name}/retriever-info.json"

    def _load_retriever_info(self, name: str) -> Dict:
        info_path = self._get_retriever_info_path(name)
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                return json.load(f)
        return {"name": name, "files": {}}

    def _save_retriever_info(self, name: str, info: Dict):
        info_path = self._get_retriever_info_path(name)
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)

    def _check_for_updates(self, name: str) -> bool:
        info = self._load_retriever_info(name)
        directory = f"/data/imported/{name}"
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            self._save_retriever_info(name, info)
            return False

        has_updates = False
        current_files = set(os.listdir(directory))
        stored_files = set(info["files"].keys())

        # Check for new or modified files
        for file in current_files:
            file_path = os.path.join(directory, file)
            if file.startswith('.') or not os.path.isfile(file_path):
                continue
            last_modified = os.path.getmtime(file_path)
            if file not in stored_files or last_modified != info["files"][file]:
                has_updates = True
                info["files"][file] = last_modified

        # Check for deleted files
        for file in stored_files - current_files:
            has_updates = True
            del info["files"][file]

        self._save_retriever_info(name, info)
        return has_updates

    def process_documents(self, name: str):
        if self._check_for_updates(name):
            self._delete_collection(name)

        directory = f"/data/imported/{name}"
        collection_name = f"{name}_collection"

        if collection_name in self.client.list_collections():
            print(f"Collection {collection_name} is up to date. Skipping processing.")
            return

        documents = []
        for filename in os.listdir(directory):
            if filename.startswith('.') or os.path.isdir(os.path.join(directory, filename)):
                continue
            file_path = os.path.join(directory, filename)
            try:
                documents.extend(self._load_document(file_path))
            except ValueError as e:
                print(f"Skipping file {filename}: {str(e)}")

        if not documents:
            print(f"No valid documents found in {directory}.")
            return

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

    def _delete_collection(self, name: str):
        collection_name = f"{name}_collection"
        if collection_name in self.client.list_collections():
            self.client.delete_collection(collection_name)
            print(f"Deleted existing collection: {collection_name}")

    def get_retriever(self, name: str):
        self.process_documents(name)  # Ensure the collection is up-to-date
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