"""
Document Loader Module for Ask Druk
Simplified version focused on local knowledge base files
"""

import os
import logging
import tempfile
import uuid
import shutil
import datetime
import json
from typing import List, Dict, Optional, BinaryIO, Tuple, Any
from pathlib import Path
from fastapi import UploadFile
from llama_index.core import SimpleDirectoryReader, Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Directory for temp file storage
TEMP_DIR = os.path.join(tempfile.gettempdir(), "druk_chatbot_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

class DocumentLoader:
    """Handles document loading for Bhutan knowledge base"""
    
    def __init__(self):
        """Initialize the document loader"""
        self.supported_extensions = [
            ".pdf", 
            ".docx", 
            ".txt", 
            ".csv", 
            ".json",
            ".md",
            ".html",
            ".pptx",
            ".xlsx",
        ]
    
    async def process_upload(self, file: UploadFile) -> Tuple[List[Document], List[str]]:
        """
        Process an uploaded file and convert it to documents
        
        Args:
            file: The uploaded file
            
        Returns:
            List of Document objects and debug info
        """
        try:
            # Get original filename
            original_filename = file.filename
            base_filename, ext = os.path.splitext(original_filename)
            ext = ext.lower()
            
            if ext not in self.supported_extensions:
                logging.warning(f"Unsupported file type: {ext}")
                return [], [f"Unsupported file type: {ext}. Supported types: {', '.join(self.supported_extensions)}"]
            
            # Create a unique file ID
            file_id = str(uuid.uuid4())
            temp_file_path = os.path.join(TEMP_DIR, f"{file_id}{ext}")
            
            # Save the file temporarily
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            debug_info = [f"Processing file: {original_filename}"]
            
            try:
                # Use SimpleDirectoryReader to load the document
                reader = SimpleDirectoryReader(
                    input_files=[temp_file_path],
                    filename_as_id=True,
                )
                
                documents = reader.load_data()
                
                # Add additional metadata to each document
                for doc in documents:
                    # Store the original filename and other metadata
                    if not hasattr(doc, 'metadata') or doc.metadata is None:
                        doc.metadata = {}
                    
                    doc.metadata.update({
                        "source": original_filename,
                        "file_type": ext[1:],  # Remove the dot
                        "upload_date": datetime.datetime.now().isoformat(),
                        "category": "uploaded_document"
                    })
                
                debug_info.append(f"Successfully loaded {len(documents)} document(s) from {file.filename}")
                
                # Clean up temporary file
                os.remove(temp_file_path)
                
                return documents, debug_info
                
            except Exception as e:
                logging.error(f"Error loading document: {str(e)}")
                debug_info.append(f"Error loading document: {str(e)}")
                
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                
                return [], debug_info
                
        except Exception as e:
            logging.error(f"Error processing upload: {str(e)}")
            return [], [f"Error processing file: {str(e)}"]
    
    def load_from_directory(self, directory: str, recursive: bool = False) -> Tuple[List[Document], List[str]]:
        """
        Load all documents from a directory
        
        Args:
            directory: The directory to load documents from
            recursive: Whether to recursively search subdirectories
            
        Returns:
            List of Document objects and debug info
        """
        try:
            debug_info = [f"Loading documents from directory: {directory}"]
            
            if not os.path.exists(directory):
                logging.warning(f"Directory does not exist: {directory}")
                return [], [f"Directory does not exist: {directory}"]
            
            # Handle JSON files specially for Bhutan knowledge base
            all_documents = []
            
            if recursive:
                # Walk through directory recursively
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        docs, file_debug = self._load_single_file(file_path, directory)
                        all_documents.extend(docs)
                        debug_info.extend(file_debug)
            else:
                # Just load files in the current directory
                for file_path in Path(directory).iterdir():
                    if file_path.is_file():
                        docs, file_debug = self._load_single_file(str(file_path), directory)
                        all_documents.extend(docs)
                        debug_info.extend(file_debug)
            
            debug_info.append(f"Successfully loaded {len(all_documents)} document(s) from directory")
            
            return all_documents, debug_info
            
        except Exception as e:
            logging.error(f"Error loading from directory: {str(e)}")
            return [], [f"Error loading from directory: {str(e)}"]
    
    def _load_single_file(self, file_path: str, base_directory: str) -> Tuple[List[Document], List[str]]:
        """Load a single file and return documents"""
        debug_info = []
        documents = []
        
        try:
            file_name = os.path.basename(file_path)
            _, ext = os.path.splitext(file_name)
            ext = ext.lower()
            
            if ext not in self.supported_extensions:
                return [], [f"Skipping unsupported file: {file_name}"]
            
            # Special handling for JSON files (Bhutan knowledge base)
            if ext == '.json':
                documents = self._load_json_as_document(file_path, base_directory)
                debug_info.append(f"Loaded JSON knowledge file: {file_name}")
            else:
                # Use SimpleDirectoryReader for other file types
                reader = SimpleDirectoryReader(
                    input_files=[file_path],
                    filename_as_id=True,
                )
                
                documents = reader.load_data()
                debug_info.append(f"Loaded document: {file_name}")
            
            # Add metadata to all documents
            for doc in documents:
                if not hasattr(doc, 'metadata') or doc.metadata is None:
                    doc.metadata = {}
                
                # Determine category based on directory structure
                relative_path = os.path.relpath(file_path, base_directory)
                category = self._determine_category(relative_path)
                
                doc.metadata.update({
                    "source": file_name,
                    "file_type": ext[1:],
                    "load_date": datetime.datetime.now().isoformat(),
                    "category": category,
                    "file_path": file_path
                })
            
            return documents, debug_info
            
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {str(e)}")
            return [], [f"Error loading {file_name}: {str(e)}"]
    
    def _load_json_as_document(self, file_path: str, base_directory: str) -> List[Document]:
        """Load JSON file as a structured document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to readable text format
            if isinstance(data, dict):
                # Handle service guides
                if 'service_name' in data:
                    content = self._format_service_guide(data)
                # Handle rights information
                elif 'rights' in data:
                    content = self._format_rights_info(data)
                # Handle office information
                elif 'office_name' in data or 'name' in data:
                    content = self._format_office_info(data)
                else:
                    # Generic JSON formatting
                    content = self._format_generic_json(data)
            elif isinstance(data, list):
                content = self._format_json_list(data)
            else:
                content = str(data)
            
            # Create document
            doc = Document(
                text=content,
                metadata={
                    "json_structure": True,
                    "original_data": data
                }
            )
            
            return [doc]
            
        except Exception as e:
            logging.error(f"Error loading JSON file {file_path}: {str(e)}")
            return []
    
    def _format_service_guide(self, data: dict) -> str:
        """Format service guide JSON into readable text"""
        content = f"Service: {data.get('service_name', 'Unknown Service')}\n\n"
        
        if 'category' in data:
            content += f"Category: {data['category']}\n\n"
        
        if 'steps' in data:
            content += "Steps to follow:\n"
            for step in data['steps']:
                step_num = step.get('step_number', '')
                title = step.get('title', '')
                desc = step.get('description', '')
                content += f"{step_num}. {title}\n   {desc}\n"
                
                if 'documents_required' in step:
                    content += f"   Required documents: {', '.join(step['documents_required'])}\n"
                if 'time_estimate' in step:
                    content += f"   Time needed: {step['time_estimate']}\n"
                content += "\n"
        
        if 'total_time' in data:
            content += f"Total processing time: {data['total_time']}\n"
        
        if 'fees' in data:
            content += f"Fees: {data['fees']}\n"
        
        if 'offices' in data:
            content += f"Available at: {', '.join(data['offices'])}\n"
        
        if 'tips' in data:
            content += "\nHelpful tips:\n"
            for tip in data['tips']:
                content += f"• {tip}\n"
        
        return content
    
    def _format_rights_info(self, data: dict) -> str:
        """Format rights information JSON into readable text"""
        content = f"Rights Information: {data.get('category', 'General Rights')}\n\n"
        
        if 'scenario' in data:
            content += f"Scenario: {data['scenario']}\n\n"
        
        if 'rights' in data:
            content += "Your rights:\n"
            for right in data['rights']:
                content += f"• {right}\n"
            content += "\n"
        
        if 'relevant_laws' in data:
            content += f"Relevant laws: {', '.join(data['relevant_laws'])}\n\n"
        
        if 'next_steps' in data:
            content += "What you can do:\n"
            for step in data['next_steps']:
                content += f"• {step}\n"
            content += "\n"
        
        if 'simplified_explanation' in data:
            content += f"In simple terms: {data['simplified_explanation']}\n"
        
        return content
    
    def _format_office_info(self, data: dict) -> str:
        """Format office information JSON into readable text"""
        name = data.get('office_name') or data.get('name', 'Unknown Office')
        content = f"Office: {name}\n\n"
        
        if 'services' in data:
            content += f"Services provided: {', '.join(data['services'])}\n"
        
        if 'address' in data:
            content += f"Address: {data['address']}\n"
        
        if 'contact' in data:
            content += f"Phone: {data['contact']}\n"
        
        if 'email' in data:
            content += f"Email: {data['email']}\n"
        
        if 'hours' in data:
            content += f"Office hours: {data['hours']}\n"
        
        if 'dzongkhag' in data:
            content += f"Dzongkhag: {data['dzongkhag']}\n"
        
        return content
    
    def _format_generic_json(self, data: dict) -> str:
        """Format generic JSON into readable text"""
        content = ""
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                content += f"{key.replace('_', ' ').title()}: {json.dumps(value, indent=2)}\n"
            else:
                content += f"{key.replace('_', ' ').title()}: {value}\n"
        return content
    
    def _format_json_list(self, data: list) -> str:
        """Format JSON list into readable text"""
        content = ""
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                content += f"Item {i}:\n"
                content += self._format_generic_json(item)
                content += "\n"
            else:
                content += f"{i}. {item}\n"
        return content
    
    def _determine_category(self, relative_path: str) -> str:
        """Determine document category based on file path"""
        path_parts = relative_path.lower().split(os.sep)
        
        if 'services' in path_parts:
            return 'government_service'
        elif 'rights' in path_parts:
            return 'citizen_rights'
        elif 'laws' in path_parts or 'legal' in path_parts:
            return 'legal_information'
        elif 'offices' in path_parts:
            return 'office_information'
        else:
            return 'general_information'
