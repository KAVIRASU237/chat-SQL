import os
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
        return len(documents)

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
        
        # Retrieve logical top-k matches for tables
        docs = self.vectorstore.similarity_search(query, k=k)
        
        context = "### DATABASE SCHEMA ###\n\n"
        for i, doc in enumerate(docs):
            context += f"TABLE {i+1}:\n{doc.page_content}\n"
            context += "-" * 20 + "\n"
        
        return context
