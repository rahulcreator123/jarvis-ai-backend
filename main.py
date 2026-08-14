import os
from typing import Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.getenv("PORT", "8000"))

# OpenRouter free model router
MODEL_NAME = "openrouter/free"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Jarvis AI Cloud Backend",
    description="Cloud AI backend for Jarvis Android",
    version="4.0.0"
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
        "provider": "OpenRouter",
        "model": MODEL_NAME
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "openrouter_configured": bool(OPENROUTER_API_KEY),
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

    if not OPENROUTER_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY is not configured on the server."
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
Do not claim that you performed an action on the Android device
unless the Android application actually performed that action.

Do not pretend to have access to phone sensors, camera,
microphone, files, contacts, messages, or applications unless
the Android application explicitly provides that information.
"""

    # --------------------------------------------------------
    # OpenRouter request
    # --------------------------------------------------------

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis-ai-backend-o4d3.onrender.com",
        "X-Title": "Jarvis AI"
    }

    # --------------------------------------------------------
    # Call OpenRouter
    # --------------------------------------------------------

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        # ----------------------------------------------------
        # Handle OpenRouter errors
        # ----------------------------------------------------

        if response.status_code != 200:

            print("========================================")
            print("OPENROUTER ERROR")
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text)
            print("========================================")

            try:
                error_data = response.json()
            except Exception:
                error_data = response.text

            raise HTTPException(
                status_code=500,
                detail=f"OpenRouter request failed: {error_data}"
            )

        # ----------------------------------------------------
        # Parse response
        # ----------------------------------------------------

        data = response.json()

        answer = (
            data
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )

        if not answer:

            raise HTTPException(
                status_code=500,
                detail="OpenRouter returned an empty response."
            )

        return ChatResponse(
            response=answer.strip(),
            model=MODEL_NAME,
            provider="OpenRouter"
        )

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="OpenRouter request timed out."
        )

    except requests.exceptions.RequestException as e:

        print("========================================")
        print("NETWORK ERROR")
        print(repr(e))
        print("========================================")

        raise HTTPException(
            status_code=500,
            detail=f"OpenRouter network error: {str(e)}"
        )

    except HTTPException:

        raise

    except Exception as e:

        print("========================================")
        print("UNEXPECTED ERROR")
        print(repr(e))
        print("========================================")

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {str(e)}"
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
