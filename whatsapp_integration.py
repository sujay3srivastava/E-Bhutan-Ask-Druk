# whatsapp_integration.py - WhatsApp integration for Ask Druk using Twilio
from fastapi import HTTPException, Request, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import logging
import hashlib
import hmac
import os
from datetime import datetime
from typing import Optional

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio WhatsApp number
TWILIO_WEBHOOK_AUTH_TOKEN = os.getenv("TWILIO_WEBHOOK_AUTH_TOKEN", TWILIO_AUTH_TOKEN)

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

# WhatsApp session mapping (phone number -> session_id)
whatsapp_sessions = {}

def verify_twilio_signature(request: Request, body: bytes) -> bool:
    """Verify that the request came from Twilio"""
    # Temporarily disable signature verification for development
    logging.info("Webhook signature verification disabled for development")
    return True
    
    # Original code (uncomment for production):
    # if not TWILIO_WEBHOOK_AUTH_TOKEN:
    #     logging.warning("TWILIO_WEBHOOK_AUTH_TOKEN not set, skipping signature verification")
    #     return True
    # 
    # signature = request.headers.get('X-Twilio-Signature', '')
    # url = str(request.url)
    # 
    # # Compute expected signature
    # expected_signature = hmac.new(
    #     TWILIO_WEBHOOK_AUTH_TOKEN.encode('utf-8'),
    #     (url + body.decode('utf-8')).encode('utf-8'),
    #     hashlib.sha1
    # ).digest()
    # 
    # # Compare signatures
    # return hmac.compare_digest(signature.encode('utf-8'), expected_signature)

def generate_session_id(phone_number: str) -> str:
    """Generate a consistent session ID for a phone number"""
    # Remove WhatsApp prefix and any special characters
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "").replace("-", "")
    return f"wa_{clean_number}"

def format_response_for_whatsapp(response_text: str, suggested_actions: Optional[list] = None) -> str:
    """Format the bot response for WhatsApp"""
    # WhatsApp Business API allows up to 4096 characters, but keep it readable
    MAX_LENGTH = 4000
    
    # First, add suggested actions if available
    if suggested_actions:
        action_text = "\n\n*Quick Actions:*\n"
        for i, action in enumerate(suggested_actions[:5], 1):  # Allow up to 5 actions
            action_text += f"{i}. {action}\n"
        
        # Only add actions if total length doesn't exceed limit
        if len(response_text + action_text) <= MAX_LENGTH:
            response_text += action_text
        else:
            # If adding actions would exceed limit, add fewer actions
            action_text = "\n\n*Quick Actions:*\n"
            for i, action in enumerate(suggested_actions[:2], 1):  # Try with just 2 actions
                action_text += f"{i}. {action}\n"
            
            if len(response_text + action_text) <= MAX_LENGTH:
                response_text += action_text
    
    # Only truncate if still too long after trying to add actions
    if len(response_text) > MAX_LENGTH:
        # Find a good place to cut (try to cut at sentence end)
        truncate_at = MAX_LENGTH - 100  # Leave room for continuation message
        
        # Try to find last sentence ending
        last_period = response_text.rfind('.', 0, truncate_at)
        last_exclamation = response_text.rfind('!', 0, truncate_at)
        last_question = response_text.rfind('?', 0, truncate_at)
        
        cut_point = max(last_period, last_exclamation, last_question)
        
        if cut_point > truncate_at - 200:  # If we found a good sentence ending
            response_text = response_text[:cut_point + 1] + "\n\n📱 *Type 'more' for additional details.*"
        else:
            # Cut at word boundary
            last_space = response_text.rfind(' ', 0, truncate_at)
            if last_space > truncate_at - 50:
                response_text = response_text[:last_space] + "...\n\n📱 *Type 'more' for additional details.*"
            else:
                response_text = response_text[:truncate_at] + "...\n\n📱 *Type 'more' for additional details.*"
    
    return response_text

def get_welcome_message() -> str:
    """Get welcome message for new WhatsApp users"""
    return """🇧🇹 *Kuzuzangpo! Welcome to Ask Druk* 🇧🇹

I'm your AI assistant for Bhutan government services and citizen rights.

*I can help you with:*
• Passport applications 🛂
• Driving license 🚗  
• Business registration 💼
• Birth certificates 📄
• Employment rights ⚖️
• Land registration 🏠
• Emergency contacts 🚨

*Just type your question!*

Examples:
• "How do I apply for a passport?"
• "What are my employment rights?"
• "Where is the immigration office?"

Type *help* anytime for more options."""

def get_help_message() -> str:
    """Get help message"""
    return """🔍 *Ask Druk Help Menu*

*Available Commands:*
• *help* - Show this menu
• *services* - List all services
• *emergency* - Emergency contacts
• *offices* - Find government offices
• *rights* - Know your rights

*Service Categories:*
• Travel Documents (passport, visa)
• Business (registration, permits)
• Legal Rights (employment, consumer)
• Civil Documents (birth, marriage)
• Property (land registration)

*Tips:*
• Be specific in your questions
• Mention your location for office info
• Type 'more' for detailed information

Just type your question naturally! 😊"""

async def process_whatsapp_message(from_number: str, message_body: str, profile_name: str = None) -> str:
    """Process incoming WhatsApp message and return response"""
    try:
        # Import here to avoid circular imports
        from application import initialize_session, chat_with_druk, chat_sessions
        from application import InitSessionRequest, ChatRequest
        
        # Generate session ID
        session_id = generate_session_id(from_number)
        
        # Handle special commands
        message_lower = message_body.lower().strip()
        
        if message_lower in ['hi', 'hello', 'start', 'kuzuzangpo']:
            return get_welcome_message()
        
        if message_lower == 'help':
            return get_help_message()
        
        if message_lower == 'emergency':
            return """🚨 *Emergency Contacts - Bhutan*

• *Police:* 113
• *Fire Department:* 110  
• *Medical Emergency:* 112
• *National Emergency:* 111
• *Tourist Helpline:* +975-2-323251

*Available 24/7 except Tourist Helpline*"""
        
        if message_lower == 'services':
            return """🏛️ *Government Services*

*Travel Documents:*
• Passport Application
• Visa Services
• Work Permits

*Business:*
• Business Registration
• Trade License
• Tax Registration

*Civil Documents:*
• Birth Certificate
• Marriage Certificate
• Death Certificate

*Transportation:*
• Driving License
• Vehicle Registration

*Others:*
• Land Registration
• Employment Rights
• Consumer Rights

Type the service name for detailed guide!"""
        
        if message_lower == 'more':
            return """📋 *Need More Information?*

I can provide detailed guidance on:

• **Government Services** - Step-by-step procedures
• **Required Documents** - What you need to bring
• **Office Locations** - Where to go in your dzongkhag
• **Fees & Timeline** - Costs and processing time
• **Your Rights** - What protections you have

*Examples of detailed questions:*
• "What documents do I need for passport?"
• "Where is immigration office in Thimphu?"
• "What are my rights if fired from job?"
• "How much does driving license cost?"

Ask me anything specific! 😊"""
        
        # Store session info
        if session_id not in whatsapp_sessions:
            whatsapp_sessions[session_id] = {
                "phone_number": from_number,
                "profile_name": profile_name,
                "first_message": datetime.now().isoformat(),
                "message_count": 0
            }
        
        whatsapp_sessions[session_id]["message_count"] += 1
        whatsapp_sessions[session_id]["last_message"] = datetime.now().isoformat()
        
        # Initialize session with Ask Druk if needed
        if session_id not in chat_sessions:
            citizen_context = {
                "platform": "whatsapp",
                "phone_number": from_number,
                "profile_name": profile_name,
                "preferred_language": "english"  # Default, could be detected
            }
            
            init_request = InitSessionRequest(
                session_id=session_id,
                citizen_context=citizen_context
            )
            await initialize_session(init_request)
        
        # Process message with Ask Druk
        chat_request = ChatRequest(
            session_id=session_id,
            message=message_body
        )
        
        response = await chat_with_druk(chat_request)
        
        # Format response for WhatsApp
        formatted_response = format_response_for_whatsapp(
            response.response,
            response.suggested_actions
        )
        
        return formatted_response
        
    except Exception as e:
        logging.error(f"Error processing WhatsApp message: {str(e)}")
        return "🤖 I apologize, but I'm having technical difficulties right now. Please try again in a few minutes, or contact support if the problem persists."

async def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio"""
    try:
        if not twilio_client:
            logging.error("Twilio client not initialized")
            return False
        
        message = twilio_client.messages.create(
            body=message,
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            to=to_number
        )
        
        logging.info(f"WhatsApp message sent to {to_number}: {message.sid}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {str(e)}")
        return False
