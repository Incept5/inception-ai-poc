import os
import json
from typing import List, Dict
import aiofiles
from langchain_community.document_loaders import PyPDFLoader, UnstructuredXMLLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import chromadb
from utils.debug_utils import debug_print
from .retriever_config import retriever_config
import asyncio

class VectorDBLoader:
    def __init__(self):
        self.client = None

    async def initialize_client(self):
        debug_print(f"Initializing ChromaDB client with persistence directory: {retriever_config.persist_directory}")
        os.makedirs(retriever_config.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=retriever_config.persist_directory)

    async def load_document(self, file_path: str):
        debug_print(f"Loading document: {file_path}")
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            return await asyncio.to_thread(PyPDFLoader(file_path).load)
        elif file_extension == ".xml":
            return await asyncio.to_thread(UnstructuredXMLLoader(file_path).load)
        elif file_extension == ".txt":
            return await asyncio.to_thread(TextLoader(file_path).load)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    def get_retriever_info_path(self, name: str):
        return f"/data/imported/{name}/retriever-info.json"

    async def load_retriever_info(self, name: str) -> Dict:
        info_path = self.get_retriever_info_path(name)
        debug_print(f"Loading retriever info from: {info_path}")
        if os.path.exists(info_path):
            async with aiofiles.open(info_path, 'r') as f:
                content = await f.read()
                info = json.loads(content)
                debug_print(f"Loaded retriever info: {info}")
                if "files" not in info or not isinstance(info["files"], list):
                    info["files"] = []
                return info
        debug_print(f"No existing retriever info found for {name}")
        return {"name": name, "files": [], "embedding_provider": retriever_config.default_embedding_provider, "embedding_model": retriever_config.default_embedding_model}

    async def save_retriever_info(self, name: str, info: Dict):
        info_path = self.get_retriever_info_path(name)
        debug_print(f"Saving retriever info to: {info_path}")
        async with aiofiles.open(info_path, 'w') as f:
            await f.write(json.dumps(info, indent=2))
        debug_print(f"Saved retriever info: {info}")

    async def check_for_updates(self, name: str) -> bool:
        debug_print(f"Checking for updates in retriever: {name}")
        info = await self.load_retriever_info(name)
        directory = f"/data/imported/{name}"

        if not os.path.exists(directory):
            debug_print(f"Creating new directory: {directory}")
            os.makedirs(directory)
            await self.save_retriever_info(name, info)
            return True

        has_updates = False
        current_files = set(os.listdir(directory))
        stored_files = {file["filename"] for file in info["files"] if isinstance(file, dict) and "filename" in file}

        debug_print(f"Current files: {current_files}")
        debug_print(f"Stored files: {stored_files}")

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

        info["files"] = [file for file in info["files"] if
                         isinstance(file, dict) and file.get("filename") in current_files]

        if info.get("embedding_provider") != retriever_config.default_embedding_provider or info.get("embedding_model") != retriever_config.default_embedding_model:
            debug_print(f"Embedding provider or model has changed. Provider: {retriever_config.default_embedding_provider}, Model: {retriever_config.default_embedding_model}")
            has_updates = True
            info["embedding_provider"] = retriever_config.default_embedding_provider
            info["embedding_model"] = retriever_config.default_embedding_model

        await self.save_retriever_info(name, info)
        debug_print(f"Updates check complete. Has updates: {has_updates}")
        return has_updates

    async def process_documents(self, name: str):
        debug_print(f"Processing documents for retriever: {name}")
        collection_name = f"{name}_collection"
        
        if not await self.check_for_updates(name):
            if await self.verify_collection_exists(name):
                debug_print(f"Collection {collection_name} is up to date. Skipping processing.")
                return
        else:
            debug_print(f"Updates detected, deleting existing collection for {name}")
            await self.delete_collection(name)

        directory = f"/data/imported/{name}"

        documents = []
        for filename in os.listdir(directory):
            if filename.startswith('.') or os.path.isdir(
                    os.path.join(directory, filename)) or filename == "retriever-info.json":
                continue
            file_path = os.path.join(directory, filename)
            try:
                documents.extend(await self.load_document(file_path))
            except ValueError as e:
                debug_print(f"Skipping file {filename}: {str(e)}")

        if not documents:
            debug_print(f"No valid documents found in {directory}.")
            return

        debug_print(f"Splitting {len(documents)} documents")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = await asyncio.to_thread(text_splitter.split_documents, documents)
        debug_print(f"Created {len(splits)} splits")

        debug_print(f"Creating Chroma vectorstore for {collection_name}")
        try:
            vectorstore = await asyncio.to_thread(
                Chroma.from_documents,
                documents=splits,
                embedding=retriever_config.get_embeddings(),
                client=self.client,
                collection_name=collection_name,
            )
            debug_print(f"Processed and persisted {len(splits)} chunks for {name}")
            
            if await self.verify_collection_exists(name):
                debug_print(f"Successfully created and verified collection: {collection_name}")
            else:
                raise Exception(f"Collection {collection_name} was not created successfully")
        except Exception as e:
            debug_print(f"Error creating Chroma vectorstore: {str(e)}")
            raise

    async def delete_collection(self, name: str):
        collection_name = f"{name}_collection"
        try:
            if collection_name in self.client.list_collections():
                debug_print(f"Deleting existing collection: {collection_name}")
                await asyncio.to_thread(self.client.delete_collection, collection_name)
                debug_print(f"Deleted collection: {collection_name}")
        except Exception as e:
            debug_print(f"Error deleting collection {collection_name}: {str(e)}")

    async def verify_collection_exists(self, name: str) -> bool:
        collection_name = f"{name}_collection"
        try:
            collections = await asyncio.to_thread(self.client.list_collections)
            exists = collection_name in [c.name for c in collections]
            if exists:
                debug_print(f"Verified: Collection {collection_name} exists")
            else:
                debug_print(f"Error: Collection {collection_name} does not exist")
            return exists
        except Exception as e:
            debug_print(f"Error verifying collection existence: {str(e)}")
            return False

vector_db_loader = VectorDBLoader()