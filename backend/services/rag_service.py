import os
import hashlib
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from backend.utils.schema_extractor import SchemaExtractor

class RAGService:
    def __init__(self, db_path: str, vector_store_path: str, ollama_url: str = "http://localhost:11434"):
        self.db_path = db_path
        self.vector_store_path = vector_store_path
        self.embeddings = OllamaEmbeddings(
            model="mistral",
            base_url=ollama_url
        )
        self.vectorstore = None

    def index_schema(self):
        """Extract schema and store in FAISS."""
        extractor = SchemaExtractor(self.db_path)
        schema_docs = extractor.get_schema_docs()
        
        documents = [Document(page_content=doc) for doc in schema_docs]
        
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.vectorstore.save_local(self.vector_store_path)

        # Save schema hash
        schema_hash = self._get_schema_hash()
        os.makedirs(self.vector_store_path, exist_ok=True)
        with open(os.path.join(self.vector_store_path, "schema.hash"), "w") as f:
            f.write(schema_hash)

        return len(documents)

    def _get_schema_hash(self) -> str:
        """Generates an MD5 hash of the current database schema."""
        extractor = SchemaExtractor(self.db_path)
        schema_docs = extractor.get_schema_docs()
        schema_string = "\n".join(schema_docs)
        return hashlib.md5(schema_string.encode()).hexdigest()

    def _schema_changed(self) -> bool:
        """Checks if the database schema has changed since the last index."""
        hash_file = os.path.join(self.vector_store_path, "schema.hash")

        if not os.path.exists(hash_file):
            return True

        with open(hash_file, "r") as f:
            stored_hash = f.read()

        current_hash = self._get_schema_hash()
        return stored_hash != current_hash

    def load_index(self):
        """Loads the FAISS index from disk."""
        if os.path.exists(self.vector_store_path):
            self.vectorstore = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        return False

    def retrieve_schema(self, query: str, k: int = 10) -> str:
        """Retrieves relevant schema parts for a query."""
        if not self.vectorstore:
            if not self.load_index():
                self.index_schema()

        # Auto re-index if schema has changed
        if self._schema_changed():
            self.index_schema()
        
        # Retrieve logical top-k matches for tables
        docs = self.vectorstore.similarity_search(query, k=k)
        
        context = "### DATABASE SCHEMA ###\n\n"
        for i, doc in enumerate(docs):
            context += f"TABLE {i+1}:\n{doc.page_content}\n"
            context += "-" * 20 + "\n"
        
        return context
