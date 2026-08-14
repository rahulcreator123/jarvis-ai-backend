import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", "8000"))

MODEL_NAME = "gemini-3.5-flash"

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


app = FastAPI(
    title="Jarvis AI Cloud Backend",
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Jarvis AI Cloud Backend",
        "provider": "Google Gemini",
        "model": MODEL_NAME
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY),
        "model": MODEL_NAME
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured."
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        system_prompt = """
You are Jarvis, a personal AI assistant.

Personality:
- Intelligent
- Friendly
- Calm
- Helpful
- Concise
- Natural

You are the cloud AI for an Android assistant.

Answer the user's request directly.
Do not claim that you performed actions on the phone unless
the Android application actually performs that action.
"""

        prompt = f"""
{system_prompt}

USER:
{request.message}
"""

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

        print("Gemini error:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"Gemini request failed: {str(e)}"
        )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )