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
        api_key=GEMINI_API_KEY,
        http_options={
            "api_version": "v1"
        }
    )


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Jarvis AI Cloud Backend",
    description="Cloud AI backend for the Jarvis Android application",
    version="2.0.0"
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
# REQUEST / RESPONSE MODELS
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
# HEALTH CHECK
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

    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    if not GEMINI_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured on the server."
        )

    # --------------------------------------------------------
    # Check Gemini client
    # --------------------------------------------------------

    if client is None:

        raise HTTPException(
            status_code=500,
            detail="Gemini client was not initialized."
        )

    # --------------------------------------------------------
    # Check message
    # --------------------------------------------------------

    if not request.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # --------------------------------------------------------
    # Jarvis personality
    # --------------------------------------------------------

    system_prompt = """
You are Jarvis, a personal AI assistant.

Your personality:
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

Important:
Do not claim that you performed an action on the Android phone
unless the Android application actually performed that action.

Do not pretend to have access to phone sensors, camera,
microphone, files, contacts, messages, or applications unless
the Android application explicitly provides that information.
"""

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = f"""
{system_prompt}

USER MESSAGE:
{request.message}
"""

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    try:

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt
        )

        answer = interaction.output_text

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
