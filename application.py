# application.py - Ask Druk - Bhutan's Sovereign AI Citizen Assistant
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional, Literal
import logging
import uvicorn
import tempfile 
import shutil
import uuid
import re

# Import helpers (adapted from EmbeddedChatbot)
from document_loader import DocumentLoader
from index_manager import IndexManager
from druk_system_prompt import DRUK_SYSTEM_PROMPT, get_citizen_context_prompt
from azure_helpers import parse_azure_error, get_user_friendly_error_message, create_safe_chat_prompt

# Import WhatsApp integration
from whatsapp_integration import (
    verify_twilio_signature, 
    process_whatsapp_message, 
    send_whatsapp_message,
    whatsapp_sessions
)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
api_key = os.getenv("AZURE_API_KEY")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_version = os.getenv("AZURE_API_VERSION")
azure_endpoint_embedding = os.getenv("AZURE_ENDPOINT_EMBEDDING")

# Initialize FastAPI app
app = FastAPI(title="Ask Druk - Bhutan's AI Citizen Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store chat sessions
chat_sessions = {}

# Initialize document loader and index manager
document_loader = DocumentLoader()
index_manager = IndexManager(
    document_loader=document_loader,
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
    azure_endpoint_embedding=azure_endpoint_embedding,
    system_prompt=DRUK_SYSTEM_PROMPT
)

# Pydantic models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    query_type: Optional[str] = None  # rights_inquiry, service_guide, etc.

class ChatResponse(BaseModel):
    session_id: str
    response: str
    query_type: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    office_locations: Optional[List[Dict]] = None
    debug_info: Optional[List[str]] = None

class InitSessionRequest(BaseModel):
    session_id: str
    citizen_context: Optional[Dict] = None  # Age, location, language preference

class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    available_services: Optional[List[Dict]] = None

class QuickGuideRequest(BaseModel):
    service_type: str  # passport, driving_license, business_registration, etc.

class RightsCheckRequest(BaseModel):
    scenario: str
    category: str  # employment, consumer, tenant, etc.

@app.on_event("startup")
async def startup_event():
    """Initialize application with Bhutan knowledge base"""
    logging.info("Starting Ask Druk - Bhutan's AI Citizen Assistant")
    
    try:
        # Load pre-built knowledge base from local files
        await load_bhutan_knowledge_base()
        
        # Initialize the index manager
        await index_manager.initialize()
        
        logging.info("Ask Druk initialized successfully with Bhutan knowledge base")
    except Exception as e:
        logging.error(f"Error initializing Ask Druk: {str(e)}")

async def load_bhutan_knowledge_base():
    """Load Bhutan-specific documents from knowledge_base directory"""
    try:
        knowledge_base_path = Path("knowledge_base")
        
        if knowledge_base_path.exists():
            # Load all JSON files from knowledge base
            documents, debug_info = document_loader.load_from_directory(
                str(knowledge_base_path), recursive=True
            )
            
            if documents:
                add_debug_info = await index_manager.add_documents(documents)
                debug_info.extend(add_debug_info)
                logging.info(f"Loaded {len(documents)} documents from Bhutan knowledge base")
            
        else:
            logging.warning("Knowledge base directory not found. Creating sample files...")
            await create_sample_knowledge_base()
            
    except Exception as e:
        logging.error(f"Error loading Bhutan knowledge base: {str(e)}")

@app.post("/initialize-session", response_model=SessionResponse)
async def initialize_session(request: InitSessionRequest):
    """Initialize a chat session with citizen context"""
    try:
        session_id = request.session_id
        
        # Store citizen context for personalized responses
        chat_sessions[session_id] = {
            "citizen_context": request.citizen_context or {},
            "query_history": [],
            "debug_info": ["Druk session initialized"]
        }
        
        # Get available services for this citizen
        available_services = get_available_services(request.citizen_context)
        
        return SessionResponse(
            session_id=session_id,
            status="initialized",
            message="Kuzuzangpo! Welcome to Ask Druk. I'm here to help you with government services and your rights as a Bhutanese citizen.",
            available_services=available_services
        )
    except Exception as e:
        logging.error(f"Error initializing session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initializing session: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_druk(request: ChatRequest):
    """Main chat endpoint with Druk"""
    try:
        session_id = request.session_id
        
        # Initialize session if it doesn't exist
        if session_id not in chat_sessions:
            await initialize_session(InitSessionRequest(session_id=session_id))
        
        # Detect query type if not provided
        if not request.query_type:
            request.query_type = detect_query_type(request.message)
        
        # Create citizen-aware chat engine if not exists
        if "chat_engine" not in chat_sessions[session_id]:
            if not index_manager.global_documents:
                return ChatResponse(
                    session_id=session_id,
                    response="I apologize, but my knowledge base is not available right now. Please try again later.",
                    debug_info=["No documents in knowledge base"]
                )
            
            # Create chat engine with Druk personality
            chat_engine, debug_info = index_manager.init_chat_engine(
                session_id, 
                system_prompt=get_citizen_context_prompt(
                    chat_sessions[session_id].get("citizen_context", {})
                )
            )
            chat_sessions[session_id]["chat_engine"] = chat_engine
            chat_sessions[session_id]["debug_info"].extend(debug_info)
        
        chat_engine = chat_sessions[session_id]["chat_engine"]
        
        # Enhance prompt based on query type
        enhanced_prompt = enhance_prompt_by_type(request.message, request.query_type)
        
        # Get response from chat engine
        try:
            response = chat_engine.chat(enhanced_prompt)
            response_text = str(response)
            
            # Post-process response for Bhutanese context
            processed_response = process_druk_response(response_text, request.query_type)
            
            # Extract suggested actions and office locations
            suggested_actions = extract_suggested_actions(response_text)
            office_locations = extract_office_locations(response_text)
            
            # Store query in history
            chat_sessions[session_id]["query_history"].append({
                "query": request.message,
                "query_type": request.query_type,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            return ChatResponse(
                session_id=session_id,
                response=processed_response,
                query_type=request.query_type,
                suggested_actions=suggested_actions,
                office_locations=office_locations,
                debug_info=chat_sessions[session_id].get("debug_info")
            )
            
        except Exception as e:
            logging.error(f"Error getting response from chat engine: {str(e)}")
            return ChatResponse(
                session_id=session_id,
                response="I understand your question, but I'm having trouble accessing the specific information right now. Could you please rephrase your question or try asking about a different topic?",
                debug_info=[f"Chat engine error: {str(e)}"]
            )
            
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/quick-guide")
async def get_quick_guide(request: QuickGuideRequest):
    """Get step-by-step guide for common services"""
    try:
        # Load service-specific guide
        guide = load_service_guide(request.service_type)
        
        return {
            "service_type": request.service_type,
            "guide": guide,
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Error getting quick guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting guide: {str(e)}")

@app.post("/rights-check")
async def check_rights(request: RightsCheckRequest):
    """Check rights for specific scenarios"""
    try:
        # Load rights information
        rights_info = load_rights_info(request.category, request.scenario)
        
        return {
            "scenario": request.scenario,
            "category": request.category,
            "rights": rights_info,
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Error checking rights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking rights: {str(e)}")

@app.get("/office-finder")
async def find_office(service_type: str, dzongkhag: Optional[str] = None):
    """Find relevant government offices"""
    try:
        offices = find_government_offices(service_type, dzongkhag)
        
        return {
            "service_type": service_type,
            "dzongkhag": dzongkhag,
            "offices": offices,
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Error finding offices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding offices: {str(e)}")

@app.get("/emergency-contacts")
async def get_emergency_contacts():
    """Get emergency contact numbers"""
    return {
        "emergency_contacts": [
            {"service": "Police", "number": "113", "available": "24/7"},
            {"service": "Fire Department", "number": "110", "available": "24/7"},
            {"service": "Medical Emergency", "number": "112", "available": "24/7"},
            {"service": "National Emergency", "number": "111", "available": "24/7"},
            {"service": "Tourist Helpline", "number": "+975-2-323251", "available": "Office hours"}
        ]
    }

# WhatsApp Integration Endpoints
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook endpoint for incoming WhatsApp messages from Twilio"""
    try:
        # Get the raw body for signature verification
        body = await request.body()
        
        # Verify Twilio signature (optional but recommended for production)
        if not verify_twilio_signature(request, body):
            logging.warning("Invalid Twilio signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse form data
        form_data = await request.form()
        
        # Extract message details
        from_number = form_data.get("From", "")  # whatsapp:+1234567890
        to_number = form_data.get("To", "")      # whatsapp:+14155238886
        message_body = form_data.get("Body", "")
        profile_name = form_data.get("ProfileName", "")
        message_sid = form_data.get("MessageSid", "")
        
        logging.info(f"WhatsApp message received from {from_number}: {message_body}")
        
        # Process the message
        response_text = await process_whatsapp_message(
            from_number=from_number,
            message_body=message_body,
            profile_name=profile_name
        )
        
        # Create Twilio response
        twiml_response = MessagingResponse()
        twiml_response.message(response_text)
        
        # Log the response
        logging.info(f"WhatsApp response sent to {from_number}: {response_text[:100]}...")
        
        return Response(
            content=str(twiml_response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logging.error(f"Error in WhatsApp webhook: {str(e)}")
        
        # Return a generic error response
        twiml_response = MessagingResponse()
        twiml_response.message("🤖 Sorry, I'm experiencing technical difficulties. Please try again later.")
        
        return Response(
            content=str(twiml_response),
            media_type="application/xml",
            status_code=200  # Return 200 to avoid Twilio retries
        )

@app.post("/webhook/whatsapp/status")
async def whatsapp_status_callback(request: Request):
    """Webhook endpoint for WhatsApp message status updates"""
    try:
        form_data = await request.form()
        
        message_sid = form_data.get("MessageSid", "")
        message_status = form_data.get("MessageStatus", "")
        to_number = form_data.get("To", "")
        
        logging.info(f"WhatsApp status update: {message_sid} - {message_status} to {to_number}")
        
        # You can store status updates in database if needed
        # update_message_status(message_sid, message_status)
        
        return {"status": "ok"}
        
    except Exception as e:
        logging.error(f"Error in WhatsApp status callback: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/send-whatsapp")
async def send_whatsapp_endpoint(
    to_number: str = Form(...),
    message: str = Form(...)
):
    """Endpoint to send WhatsApp messages (for testing or admin use)"""
    try:
        # Ensure number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        success = await send_whatsapp_message(to_number, message)
        
        if success:
            return {"status": "sent", "message": "Message sent successfully"}
        else:
            return {"status": "failed", "message": "Failed to send message"}
            
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.get("/whatsapp/sessions")
async def get_whatsapp_sessions():
    """Get active WhatsApp sessions (for admin/monitoring)"""
    try:
        return {
            "total_sessions": len(whatsapp_sessions),
            "sessions": whatsapp_sessions
        }
    except Exception as e:
        logging.error(f"Error getting WhatsApp sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting sessions: {str(e)}")

# Helper functions
def detect_query_type(message: str) -> str:
    """Detect the type of query based on keywords"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["right", "rights", "fired", "unfair", "discriminat"]):
        return "rights_inquiry"
    elif any(word in message_lower for word in ["apply", "application", "register", "license", "permit"]):
        return "service_guide"
    elif any(word in message_lower for word in ["office", "where", "location", "contact"]):
        return "office_finder"
    elif any(word in message_lower for word in ["law", "legal", "regulation", "rule"]):
        return "law_explanation"
    elif any(word in message_lower for word in ["document", "documents", "need", "required"]):
        return "document_help"
    else:
        return "general_inquiry"

def enhance_prompt_by_type(message: str, query_type: str) -> str:
    """Enhance the prompt based on query type"""
    enhancements = {
        "rights_inquiry": "Please explain the citizen's rights in this situation and provide specific steps they can take: ",
        "service_guide": "Please provide a step-by-step guide for: ",
        "office_finder": "Please provide office locations and contact information for: ",
        "law_explanation": "Please explain in simple terms: ",
        "document_help": "Please list the required documents and procedures for: "
    }
    
    enhancement = enhancements.get(query_type, "")
    return enhancement + message

def process_druk_response(response: str, query_type: str) -> str:
    """Process response to match Druk's personality"""
    # Add Bhutanese greeting if not present
    if not any(greeting in response.lower() for greeting in ["kuzuzangpo", "hello", "hi"]):
        if query_type == "rights_inquiry":
            response = "I understand this situation must be stressful. " + response
        else:
            response = "I'm happy to help you with this. " + response
    
    # Ensure cultural sensitivity
    response = response.replace("I don't know", "Let me help you find the right information")
    response = response.replace("complicated", "requires careful attention")
    
    return response

def extract_suggested_actions(response: str) -> List[str]:
    """Extract action items from response"""
    actions = []
    
    # Look for numbered lists or bullet points
    import re
    
    # Pattern for numbered actions
    numbered_actions = re.findall(r'\d+\.\s*([^.\n]+)', response)
    actions.extend(numbered_actions[:5])  # Limit to 5 actions
    
    # Pattern for bullet points
    bullet_actions = re.findall(r'[-•]\s*([^.\n]+)', response)
    actions.extend(bullet_actions[:3])
    
    return actions[:5]  # Return max 5 actions

def extract_office_locations(response: str) -> List[Dict]:
    """Extract office information from response"""
    offices = []
    
    # This would be enhanced with actual office data
    if "immigration" in response.lower():
        offices.append({
            "name": "Immigration Office, Thimphu",
            "address": "Thimphu, Bhutan",
            "contact": "+975-2-322526",
            "hours": "9:00 AM - 5:00 PM (Mon-Fri)"
        })
    
    return offices

def get_available_services(citizen_context: Optional[Dict]) -> List[Dict]:
    """Get available services based on citizen context"""
    services = [
        {"name": "Passport Application", "icon": "🛂", "category": "Travel Documents"},
        {"name": "Driving License", "icon": "🚗", "category": "Transportation"},
        {"name": "Business Registration", "icon": "💼", "category": "Business"},
        {"name": "Birth Certificate", "icon": "📄", "category": "Civil Documents"},
        {"name": "Employment Rights", "icon": "⚖️", "category": "Legal Rights"},
        {"name": "Land Registration", "icon": "🏠", "category": "Property"}
    ]
    
    return services

def load_service_guide(service_type: str) -> Dict:
    """Load service guide from knowledge base"""
    # This would load from actual JSON files
    guides = {
        "passport": {
            "title": "Passport Application Guide",
            "steps": [
                {"step": 1, "title": "Gather Required Documents", "description": "Collect citizenship ID, birth certificate, and photographs", "documents": ["Citizenship ID", "Birth Certificate"], "time_estimate": "1 day"},
                {"step": 2, "title": "Visit Immigration Office", "description": "Go to Immigration Office in Thimphu with all documents", "time_estimate": "1 day"},
                {"step": 3, "title": "Submit Application", "description": "Fill out application form and submit with documents", "time_estimate": "30 minutes"},
                {"step": 4, "title": "Pay Fees", "description": "Pay passport fee (Nu. 500 for regular, Nu. 1000 for urgent)", "time_estimate": "15 minutes"},
                {"step": 5, "title": "Collect Passport", "description": "Return after 7-10 working days to collect passport", "time_estimate": "7-10 working days"}
            ],
            "total_time": "7-10 working days",
            "fees": {"regular": 500, "urgent": 1000},
            "offices": ["Immigration Office, Thimphu"],
            "tips": ["Apply early during non-peak seasons", "Bring photocopies of all documents"]
        }
    }
    
    return guides.get(service_type, {"error": "Guide not found"})

def load_rights_info(category: str, scenario: str) -> Dict:
    """Load rights information"""
    rights = {
        "employment": {
            "unfair_dismissal": {
                "rights": [
                    "Right to written notice (usually 1 month)",
                    "Right to severance pay if employed >1 year", 
                    "Right to know the reason for dismissal",
                    "Right to appeal the decision"
                ],
                "relevant_laws": ["Labour Act 2007, Section 45"],
                "next_steps": ["File complaint with Labour Ministry within 30 days"],
                "simplified_explanation": "If you're fired without cause, you have specific rights and can take action."
            }
        }
    }
    
    return rights.get(category, {}).get(scenario, {"error": "Rights information not found"})

def find_government_offices(service_type: str, dzongkhag: Optional[str] = None) -> List[Dict]:
    """Find relevant government offices"""
    offices = [
        {
            "name": "Immigration Office",
            "services": ["passport", "visa", "work_permit"],
            "address": "Thimphu, Bhutan",
            "contact": "+975-2-322526",
            "hours": "9:00 AM - 5:00 PM (Mon-Fri)",
            "dzongkhag": "Thimphu"
        }
    ]
    
    # Filter by service type and dzongkhag
    relevant_offices = []
    for office in offices:
        if service_type in office.get("services", []):
            if not dzongkhag or office.get("dzongkhag") == dzongkhag:
                relevant_offices.append(office)
    
    return relevant_offices

async def create_sample_knowledge_base():
    """Create sample knowledge base files"""
    # Create sample passport application guide
    passport_guide = {
        "id": "passport_application",
        "service_name": "Passport Application",
        "category": "Travel Documents",
        "steps": [
            {
                "step_number": 1,
                "title": "Gather Required Documents",
                "description": "You will need citizenship ID, birth certificate, and recent photographs",
                "documents_required": ["Citizenship ID", "Birth Certificate", "2 passport photos"],
                "time_estimate": "1 day"
            }
        ],
        "total_time": "7-10 working days",
        "fees": {"regular": 500, "urgent": 1000},
        "offices": ["Immigration Office, Thimphu"],
        "online_available": True,
        "tips": ["Apply early during non-peak seasons"]
    }
    
    # Save sample files
    services_dir = Path("knowledge_base/services")
    services_dir.mkdir(parents=True, exist_ok=True)
    
    with open(services_dir / "passport_application.json", "w") as f:
        json.dump(passport_guide, f, indent=2)

# Frontend routes
@app.get("/")
async def root():
    """Serve the main Druk interface"""
    return FileResponse("static/druk.html")

@app.get("/admin")
async def admin():
    """Serve the admin interface for knowledge base management"""
    return FileResponse("static/admin.html")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Ask Druk - Bhutan's AI Citizen Assistant", 
        "timestamp": datetime.datetime.now().isoformat()
    }

# For deployment
application = app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
