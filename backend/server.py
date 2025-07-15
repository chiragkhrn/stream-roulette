from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import asyncio
from datetime import datetime
import uuid
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Email Reply Assistant", description="AI-powered email reply assistant for job seekers")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "test_database")
client = MongoClient(mongo_url)
db = client[db_name]

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Collections
email_sessions = db.email_sessions
templates = db.templates

# Pydantic models
class EmailRequest(BaseModel):
    original_email: str
    context: Optional[str] = ""
    user_name: Optional[str] = ""
    email_type: Optional[str] = "general"
    tone: Optional[str] = "professional"

class EmailResponse(BaseModel):
    reply_id: str
    email_type: str
    tone: str
    reply_content: str
    timestamp: datetime

class GenerateReplyRequest(BaseModel):
    original_email: str
    context: Optional[str] = ""
    user_name: Optional[str] = ""

class GenerateReplyResponse(BaseModel):
    session_id: str
    email_type: str
    replies: List[EmailResponse]

# Email type classification prompts
EMAIL_CLASSIFICATION_PROMPT = """
Analyze the following email and classify it into one of these categories:
1. interview_invitation - Emails inviting for interviews
2. job_offer - Job offer emails
3. rejection - Rejection emails
4. follow_up - Follow-up requests or responses
5. networking - Networking emails
6. recruiter_outreach - Recruiter outreach emails
7. scheduling - Meeting/interview scheduling emails
8. general - General job-related emails

Email to classify:
{email}

Respond with only the category name (e.g., "interview_invitation").
"""

# Reply generation prompts by type and tone
REPLY_PROMPTS = {
    "interview_invitation": {
        "professional": """
You are a professional email assistant helping a job seeker respond to an interview invitation. 
Generate a professional, courteous response accepting the interview invitation.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Confirms availability and enthusiasm
- Thanks the sender
- Asks any necessary clarifying questions
- Maintains professional tone
- Is concise and clear
""",
        "enthusiastic": """
You are a professional email assistant helping a job seeker respond to an interview invitation. 
Generate an enthusiastic but professional response accepting the interview invitation.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Shows genuine excitement about the opportunity
- Confirms availability
- Thanks the sender warmly
- Demonstrates interest in the company/role
- Maintains professional boundaries
""",
        "casual": """
You are a professional email assistant helping a job seeker respond to an interview invitation. 
Generate a friendly, approachable response accepting the interview invitation.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Uses a warm, friendly tone
- Confirms availability
- Thanks the sender
- Shows personality while remaining professional
- Is conversational but respectful
"""
    },
    "job_offer": {
        "professional": """
You are a professional email assistant helping a job seeker respond to a job offer. 
Generate a professional response acknowledging the offer.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Thanks the sender for the offer
- Expresses appreciation for the opportunity
- Indicates you need time to review (if applicable)
- Asks about next steps or timeline
- Maintains professional tone
""",
        "enthusiastic": """
You are a professional email assistant helping a job seeker respond to a job offer. 
Generate an enthusiastic response to the job offer.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Shows genuine excitement about the offer
- Thanks the sender enthusiastically
- Expresses strong interest in the position
- Asks about next steps
- Maintains professional enthusiasm
""",
        "casual": """
You are a professional email assistant helping a job seeker respond to a job offer. 
Generate a warm, friendly response to the job offer.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Uses a warm, appreciative tone
- Thanks the sender genuinely
- Shows interest in the opportunity
- Asks about next steps in a friendly way
- Maintains professional friendliness
"""
    },
    "follow_up": {
        "professional": """
You are a professional email assistant helping a job seeker create a follow-up response. 
Generate a professional follow-up email.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- References the previous interaction
- Provides requested information or updates
- Maintains professional tone
- Shows continued interest
- Includes appropriate next steps
""",
        "enthusiastic": """
You are a professional email assistant helping a job seeker create a follow-up response. 
Generate an enthusiastic follow-up email.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Shows continued enthusiasm
- References the previous interaction positively
- Provides requested information eagerly
- Demonstrates strong interest
- Maintains professional enthusiasm
""",
        "casual": """
You are a professional email assistant helping a job seeker create a follow-up response. 
Generate a friendly follow-up email.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Uses a warm, friendly tone
- References the previous interaction naturally
- Provides requested information
- Shows continued interest
- Maintains conversational professionalism
"""
    },
    "networking": {
        "professional": """
You are a professional email assistant helping a job seeker respond to a networking email. 
Generate a professional networking response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Thanks the sender for reaching out
- Shows interest in connecting
- Suggests next steps for networking
- Maintains professional networking tone
- Includes relevant background briefly
""",
        "enthusiastic": """
You are a professional email assistant helping a job seeker respond to a networking email. 
Generate an enthusiastic networking response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Shows genuine excitement about connecting
- Thanks the sender warmly
- Expresses strong interest in their work/company
- Suggests next steps enthusiastically
- Maintains professional networking enthusiasm
""",
        "casual": """
You are a professional email assistant helping a job seeker respond to a networking email. 
Generate a friendly networking response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Uses a warm, approachable tone
- Thanks the sender genuinely
- Shows interest in connecting
- Suggests next steps naturally
- Maintains friendly professionalism
"""
    },
    "general": {
        "professional": """
You are a professional email assistant helping a job seeker respond to a job-related email. 
Generate a professional response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Addresses the sender's points
- Maintains professional tone
- Provides requested information
- Shows appropriate level of interest
- Includes next steps if applicable
""",
        "enthusiastic": """
You are a professional email assistant helping a job seeker respond to a job-related email. 
Generate an enthusiastic response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Shows enthusiasm for the opportunity
- Addresses the sender's points positively
- Provides requested information eagerly
- Demonstrates strong interest
- Maintains professional enthusiasm
""",
        "casual": """
You are a professional email assistant helping a job seeker respond to a job-related email. 
Generate a friendly response.

Original email: {original_email}
Context: {context}
User name: {user_name}

Create a response that:
- Uses a warm, friendly tone
- Addresses the sender's points naturally
- Provides requested information
- Shows appropriate interest
- Maintains conversational professionalism
"""
    }
}

async def classify_email(email_content: str) -> str:
    """Classify email type using OpenAI"""
    try:
        session_id = str(uuid.uuid4())
        chat = LlmChat(
            api_key=openai_api_key,
            session_id=session_id,
            system_message="You are an expert email classifier for job-related emails."
        ).with_model("openai", "gpt-4o")
        
        prompt = EMAIL_CLASSIFICATION_PROMPT.format(email=email_content)
        user_message = UserMessage(text=prompt)
        
        response = await chat.send_message(user_message)
        
        # Extract the classification from the response
        classification = response.strip().lower()
        
        # Map to valid categories
        valid_categories = ["interview_invitation", "job_offer", "rejection", "follow_up", "networking", "recruiter_outreach", "scheduling", "general"]
        
        if classification in valid_categories:
            return classification
        else:
            return "general"
            
    except Exception as e:
        logger.error(f"Error classifying email: {str(e)}")
        return "general"

async def generate_reply(email_content: str, context: str, user_name: str, email_type: str, tone: str) -> str:
    """Generate email reply using OpenAI"""
    try:
        session_id = str(uuid.uuid4())
        chat = LlmChat(
            api_key=openai_api_key,
            session_id=session_id,
            system_message="You are a professional email assistant helping job seekers write appropriate responses."
        ).with_model("openai", "gpt-4o")
        
        # Get the appropriate prompt
        if email_type in REPLY_PROMPTS and tone in REPLY_PROMPTS[email_type]:
            prompt_template = REPLY_PROMPTS[email_type][tone]
        else:
            prompt_template = REPLY_PROMPTS["general"]["professional"]
        
        prompt = prompt_template.format(
            original_email=email_content,
            context=context or "No additional context provided",
            user_name=user_name or "Job Seeker"
        )
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Error generating reply: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Email Reply Assistant"}

@app.post("/api/generate-replies", response_model=GenerateReplyResponse)
async def generate_replies(request: GenerateReplyRequest):
    """Generate multiple email replies with different tones"""
    try:
        # Classify the email type
        email_type = await classify_email(request.original_email)
        
        # Generate replies for different tones
        tones = ["professional", "enthusiastic", "casual"]
        replies = []
        
        for tone in tones:
            reply_content = await generate_reply(
                request.original_email,
                request.context,
                request.user_name,
                email_type,
                tone
            )
            
            reply = EmailResponse(
                reply_id=str(uuid.uuid4()),
                email_type=email_type,
                tone=tone,
                reply_content=reply_content,
                timestamp=datetime.now()
            )
            replies.append(reply)
        
        # Create session
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "original_email": request.original_email,
            "context": request.context,
            "user_name": request.user_name,
            "email_type": email_type,
            "replies": [reply.dict() for reply in replies],
            "created_at": datetime.now()
        }
        
        # Store session in MongoDB
        email_sessions.insert_one(session_data)
        
        return GenerateReplyResponse(
            session_id=session_id,
            email_type=email_type,
            replies=replies
        )
        
    except Exception as e:
        logger.error(f"Error in generate_replies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating replies: {str(e)}")

@app.post("/api/generate-single-reply", response_model=EmailResponse)
async def generate_single_reply(request: EmailRequest):
    """Generate a single email reply"""
    try:
        # Classify the email type if not provided
        if request.email_type == "general":
            email_type = await classify_email(request.original_email)
        else:
            email_type = request.email_type
        
        # Generate reply
        reply_content = await generate_reply(
            request.original_email,
            request.context,
            request.user_name,
            email_type,
            request.tone
        )
        
        reply = EmailResponse(
            reply_id=str(uuid.uuid4()),
            email_type=email_type,
            tone=request.tone,
            reply_content=reply_content,
            timestamp=datetime.now()
        )
        
        return reply
        
    except Exception as e:
        logger.error(f"Error in generate_single_reply: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating reply: {str(e)}")

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session data by ID"""
    try:
        session = email_sessions.find_one({"session_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Convert MongoDB ObjectId to string for JSON serialization
        session["_id"] = str(session["_id"])
        return session
        
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@app.get("/api/email-types")
async def get_email_types():
    """Get available email types"""
    return {
        "email_types": [
            {"value": "interview_invitation", "label": "Interview Invitation"},
            {"value": "job_offer", "label": "Job Offer"},
            {"value": "rejection", "label": "Rejection"},
            {"value": "follow_up", "label": "Follow-up"},
            {"value": "networking", "label": "Networking"},
            {"value": "recruiter_outreach", "label": "Recruiter Outreach"},
            {"value": "scheduling", "label": "Scheduling"},
            {"value": "general", "label": "General"}
        ]
    }

@app.get("/api/tones")
async def get_tones():
    """Get available response tones"""
    return {
        "tones": [
            {"value": "professional", "label": "Professional"},
            {"value": "enthusiastic", "label": "Enthusiastic"},
            {"value": "casual", "label": "Casual"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)