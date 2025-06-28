"""
Index Manager Module for Ask Druk
Handles creation and management of vector indices for Bhutan knowledge base
"""

import os
import logging
import json
from typing import List, Optional, Dict, Any, Tuple

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from document_loader import DocumentLoader
from druk_system_prompt import DRUK_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class IndexManager:
    """Manages the creation and retrieval of vector indices for Druk"""
    
    def __init__(self, document_loader: DocumentLoader, 
                 api_key: str, 
                 azure_endpoint: str, 
                 api_version: str,
                 azure_endpoint_embedding: str,
                 system_prompt: str = DRUK_SYSTEM_PROMPT):
        """Initialize the index manager"""
        self.document_loader = document_loader
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        self.azure_endpoint_embedding = azure_endpoint_embedding
        self.system_prompt = system_prompt
        
        # Global state
        self.global_documents = []
        self.global_index = None
        self.global_index_needs_update = False
        
        # Initialize settings
        self._init_settings()
    
    def _init_settings(self):
        """Initialize LlamaIndex settings"""
        Settings.chunk_size = 512  # Larger chunks for government information
        Settings.chunk_overlap = 50
        Settings.num_output = 2048
        
        # Azure OpenAI LLM
        llm = AzureOpenAI(
            model="gpt-4",
            deployment_name="gpt-4",
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version,
        )
        
        # Azure OpenAI Embeddings
        embed_model = AzureOpenAIEmbedding(
            model="text-embedding-3-large",
            deployment_name="text-embedding-3-large",
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint_embedding,
            api_version="2023-05-15",
        )
        
        Settings.llm = llm
        Settings.embed_model = embed_model
    
    async def initialize(self):
        """Initialize the index manager with Bhutan knowledge base"""
        try:
            logging.info("Initializing Druk knowledge base...")
            # The knowledge base will be loaded by the main application
            # This method is called after documents are loaded
        except Exception as e:
            logging.error(f"Error initializing index manager: {str(e)}")
    
    def update_global_index(self) -> bool:
        """Update the global vector index if needed"""
        try:
            # If index doesn't exist or needs update
            if self.global_index is None or self.global_index_needs_update:
                if not self.global_documents:
                    logging.warning("No documents available to create index")
                    return False
                
                # Create index from global documents
                logging.info(f"Creating Druk index from {len(self.global_documents)} documents")
                self.global_index = VectorStoreIndex.from_documents(self.global_documents)
                self.global_index_needs_update = False
                
                logging.info("Successfully created Druk knowledge base index")
                return True
            
            return True
        except Exception as e:
            logging.error(f"Error updating global index: {str(e)}")
            return False
    
    def init_chat_engine(self, session_id: str, system_prompt: Optional[str] = None) -> Tuple[Any, List[str]]:
        """Initialize a chat engine for the session using the global knowledge base"""
        try:
            # Check if the global index exists or needs updating
            if not self.update_global_index():
                raise ValueError("Druk's knowledge base is not available. Please contact support.")
            
            doc_debug_info = [f"Using Druk knowledge base with {len(self.global_documents)} documents"]
            
            # Use provided system prompt or default
            chat_system_prompt = system_prompt or self.system_prompt
                    
            # Initialize chat memory (session-specific)
            memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

            # Create chat engine with Druk's personality
            chat_engine = CondensePlusContextChatEngine.from_defaults(
                retriever=self.global_index.as_retriever(similarity_top_k=5),  # More context for government info
                memory=memory,
                verbose=True,
                system_prompt=chat_system_prompt
            )
            
            return chat_engine, doc_debug_info
        except Exception as e:
            logging.error(f"Error initializing chat engine for session {session_id}: {str(e)}")
            raise e
    
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the global knowledge base"""
        debug_info = []
        
        if documents:
            self.global_documents.extend(documents)
            self.global_index_needs_update = True
            debug_info.append(f"Added to Druk knowledge base (now {len(self.global_documents)} documents)")
            
            # Update the global index
            if self.update_global_index():
                debug_info.append("Successfully updated Druk knowledge base index")
            else:
                debug_info.append("Warning: Failed to update index")
        
        return debug_info
    
    async def remove_document(self, file_path: str) -> int:
        """Remove a document from the global knowledge base and update the index"""
        # Remove the document from the global knowledge base if it exists
        docs_to_remove = []
        for i, doc in enumerate(self.global_documents):
            if hasattr(doc, 'metadata') and doc.metadata and doc.metadata.get('file_path') == file_path:
                docs_to_remove.append(i)
        
        # If no documents to remove, return early
        if not docs_to_remove:
            return 0
            
        # Remove from highest index to lowest to avoid index shifting issues
        for i in sorted(docs_to_remove, reverse=True):
            del self.global_documents[i]
        
        # Flag the index for updating
        self.global_index_needs_update = True
        
        # Update the index
        self.update_global_index()
        
        return len(docs_to_remove)
    
    async def rebuild_index(self) -> Dict[str, Any]:
        """Manually rebuild the index from all documents"""
        try:
            if not self.global_documents:
                return {
                    "status": "warning",
                    "message": "No documents found to index"
                }
            
            # Force rebuild of index
            self.global_index_needs_update = True
            self.update_global_index()
            
            return {
                "status": "success",
                "message": f"Druk index rebuilt with {len(self.global_documents)} documents",
                "document_count": len(self.global_documents)
            }
        except Exception as e:
            logging.error(f"Error rebuilding index: {str(e)}")
            raise e
    
    async def get_index_status(self) -> Dict[str, Any]:
        """Get the status of the index"""
        try:
            return {
                "status": "success",
                "index_in_memory": self.global_index is not None,
                "needs_update": self.global_index_needs_update,
                "document_count_in_memory": len(self.global_documents),
                "categories": self._get_document_categories()
            }
        except Exception as e:
            logging.error(f"Error getting index status: {str(e)}")
            raise e
    
    def _get_document_categories(self) -> Dict[str, int]:
        """Get count of documents by category"""
        categories = {}
        for doc in self.global_documents:
            if hasattr(doc, 'metadata') and doc.metadata:
                category = doc.metadata.get('category', 'unknown')
                categories[category] = categories.get(category, 0) + 1
        return categories
