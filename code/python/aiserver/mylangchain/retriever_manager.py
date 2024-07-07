import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader, UnstructuredXMLLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
import chromadb
from utils.debug_utils import debug_print


class RetrieverManager:
    def __init__(self):
        self.embedding_provider = os.getenv("DEFAULT_EMBEDDING_PROVIDER", "openai")
        self.embedding_model = os.getenv("DEFAULT_EMBEDDING_MODEL", "text-embedding-ada-002")
        self.persist_directory = "/data/embeddings/__chromadb"
        self.embeddings = None
        self.client = None

    def check_imports(self, names: Optional[List[str]] = None):
        debug_print("Checking imports and initializing RetrieverManager")
        self._initialize_embeddings()
        self._initialize_client()
        
        if names is None:
            configured_importers = os.getenv("CONFIGURED_IMPORTERS", "")
            names = [name.strip() for name in configured_importers.split(",")] if configured_importers else []
        
        debug_print(f"Processing importers: {names}")
        for name in names:
            self.process_documents(name)

    def _initialize_embeddings(self):
        debug_print(f"Initializing embeddings for provider: {self.embedding_provider}")
        if self.embedding_provider == "openai":
            self.embeddings = OpenAIEmbeddings(model=self.embedding_model)
        elif self.embedding_provider == "huggingface":
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")

    def _initialize_client(self):
        debug_print(f"Initializing ChromaDB client with persistence directory: {self.persist_directory}")
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)

    def _load_document(self, file_path: str):
        debug_print(f"Loading document: {file_path}")
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
        debug_print(f"Loading retriever info from: {info_path}")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
                debug_print(f"Loaded retriever info: {info}")
                # Ensure the "files" key exists and is a list
                if "files" not in info or not isinstance(info["files"], list):
                    info["files"] = []
                return info
        debug_print(f"No existing retriever info found for {name}")
        return {"name": name, "files": [], "embedding_provider": self.embedding_provider, "embedding_model": self.embedding_model}

    def _save_retriever_info(self, name: str, info: Dict):
        info_path = self._get_retriever_info_path(name)
        debug_print(f"Saving retriever info to: {info_path}")
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        debug_print(f"Saved retriever info: {info}")

    def _check_for_updates(self, name: str) -> bool:
        debug_print(f"Checking for updates in retriever: {name}")
        info = self._load_retriever_info(name)
        directory = f"/data/imported/{name}"

        if not os.path.exists(directory):
            debug_print(f"Creating new directory: {directory}")
            os.makedirs(directory)
            self._save_retriever_info(name, info)
            return True

        has_updates = False
        current_files = set(os.listdir(directory))
        stored_files = {file["filename"] for file in info["files"] if isinstance(file, dict) and "filename" in file}

        debug_print(f"Current files: {current_files}")
        debug_print(f"Stored files: {stored_files}")

        # Check for new or modified files
        for file in current_files:
            file_path = os.path.join(directory, file)
            if file.startswith('.') or not os.path.isfile(file_path) or file == "retriever-info.json":
                continue
            last_modified = os.path.getmtime(file_path)
            stored_file = next(
                (item for item in info["files"] if isinstance(item, dict) and item.get("filename") == file), None)
            if not stored_file or last_modified != stored_file.get("last_modified"):
                debug_print(f"Update detected for file: {file}")
                has_updates = True
                if stored_file:
                    stored_file["last_modified"] = last_modified
                else:
                    info["files"].append({"filename": file, "last_modified": last_modified})

        # Check for deleted files
        info["files"] = [file for file in info["files"] if
                         isinstance(file, dict) and file.get("filename") in current_files]

        # Check if embedding provider or model has changed
        if info.get("embedding_provider") != self.embedding_provider or info.get("embedding_model") != self.embedding_model:
            debug_print(f"Embedding provider or model has changed. Provider: {self.embedding_provider}, Model: {self.embedding_model}")
            has_updates = True
            info["embedding_provider"] = self.embedding_provider
            info["embedding_model"] = self.embedding_model

        self._save_retriever_info(name, info)
        debug_print(f"Updates check complete. Has updates: {has_updates}")
        return has_updates

    def process_documents(self, name: str):
        debug_print(f"Processing documents for retriever: {name}")
        collection_name = f"{name}_collection"
        
        if not self._check_for_updates(name):
            if self._verify_collection_exists(name):
                debug_print(f"Collection {collection_name} is up to date. Skipping processing.")
                return
        else:
            debug_print(f"Updates detected, deleting existing collection for {name}")
            self._delete_collection(name)

        directory = f"/data/imported/{name}"

        documents = []
        for filename in os.listdir(directory):
            if filename.startswith('.') or os.path.isdir(
                    os.path.join(directory, filename)) or filename == "retriever-info.json":
                continue
            file_path = os.path.join(directory, filename)
            try:
                documents.extend(self._load_document(file_path))
            except ValueError as e:
                debug_print(f"Skipping file {filename}: {str(e)}")

        if not documents:
            debug_print(f"No valid documents found in {directory}.")
            return

        debug_print(f"Splitting {len(documents)} documents")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        debug_print(f"Created {len(splits)} splits")

        debug_print(f"Creating Chroma vectorstore for {collection_name}")
        try:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                client=self.client,
                collection_name=collection_name,
            )
            debug_print(f"Processed and persisted {len(splits)} chunks for {name}")
            
            # Verify the collection exists after storing the embeddings
            if self._verify_collection_exists(name):
                debug_print(f"Successfully created and verified collection: {collection_name}")
            else:
                raise Exception(f"Collection {collection_name} was not created successfully")
        except Exception as e:
            debug_print(f"Error creating Chroma vectorstore: {str(e)}")
            raise

    def _delete_collection(self, name: str):
        collection_name = f"{name}_collection"
        try:
            if collection_name in self.client.list_collections():
                debug_print(f"Deleting existing collection: {collection_name}")
                self.client.delete_collection(collection_name)
                debug_print(f"Deleted collection: {collection_name}")
        except Exception as e:
            debug_print(f"Error deleting collection {collection_name}: {str(e)}")

    def _verify_collection_exists(self, name: str) -> bool:
        collection_name = f"{name}_collection"
        try:
            collections = self.client.list_collections()
            exists = collection_name in [c.name for c in collections]
            if exists:
                debug_print(f"Verified: Collection {collection_name} exists")
            else:
                debug_print(f"Error: Collection {collection_name} does not exist")
            return exists
        except Exception as e:
            debug_print(f"Error verifying collection existence: {str(e)}")
            return False

    def get_retriever(self, name: str):
        debug_print(f"Getting retriever for: {name}")
        try:
            self.process_documents(name)  # Ensure the collection is up-to-date
            collection_name = f"{name}_collection"
            if not self._verify_collection_exists(name):
                debug_print(f"Error: Collection {collection_name} does not exist.")
                return None

            debug_print(f"Creating Chroma vectorstore for {collection_name}")
            vectorstore = Chroma(
                client=self.client,
                embedding_function=self.embeddings,
                collection_name=collection_name,
            )
            debug_print(f"Retriever created for {name}")
            return vectorstore.as_retriever()
        except Exception as e:
            debug_print(f"Error in get_retriever: {str(e)}")
            return None


retriever_manager = RetrieverManager()
debug_print("RetrieverManager instance created")