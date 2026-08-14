import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "8000"))

MODEL_NAME = "gemini-3.5-flash"


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Jarvis AI Cloud Backend",
    description="Cloud AI backend for Jarvis Android",
    version="3.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "Jarvis AI Cloud Backend",
        "provider": "Google Gemini",
        "model": MODEL_NAME
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "model": MODEL_NAME
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured."
        )

    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Gemini client was not initialized."
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    system_prompt = """
You are Jarvis, a personal AI assistant.

Personality:
- Intelligent
- Friendly
- Calm
- Helpful
- Natural
- Concise
- Professional

You are the cloud AI backend for an Android assistant.

Answer the user's request directly.

You can help with:
- Questions
- Coding
- Learning
- Planning
- Explanations
- General conversation
- Productivity

Do not claim to have performed actions on the Android device
unless the Android application actually performed those actions.

Do not claim access to the phone's camera, microphone, files,
contacts, messages, sensors, or applications unless the Android
application explicitly provides that information.
"""

    prompt = f"""
{system_prompt}

USER:
{request.message}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        answer = response.text

        if not answer:
            answer = "Sorry, I couldn't generate a response."

        return ChatResponse(
            response=answer.strip(),
            model=MODEL_NAME,
            provider="Google Gemini"
        )

    except Exception as e:

        print("========================================")
        print("GEMINI REQUEST ERROR")
        print(repr(e))
        print("========================================")

        raise HTTPException(
            status_code=500,
            detail=f"Gemini request failed: {str(e)}"
        )


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )
