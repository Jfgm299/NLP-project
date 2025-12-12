import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
import uuid

# === PATH SETUP ===
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.append(src_path)

# === IMPORT CREW ===
try:
    from erasmusplanner.crew import Erasmusplanner
except Exception as e:
    print("ERROR IMPORTING CREW:", e)
    raise e

load_dotenv()

app = FastAPI()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATA MODELS ===
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None  # Optional: reuse conversation

# Store Crew instances per conversation
CONVERSATIONS = {}

@app.get("/")
def root():
    return {"message": "Backend running successfully!"}

@app.post("/api/chat")
async def run_chat(request: ChatRequest):
    try:
        user_msg = request.message
        conv_id = request.conversation_id or str(uuid.uuid4())

        # Load or create Crew instance
        if conv_id in CONVERSATIONS:
            crew = CONVERSATIONS[conv_id]
        else:
            crew_builder = Erasmusplanner()
            crew = crew_builder.crew()
            CONVERSATIONS[conv_id] = crew

        # === Prepare inputs ===
        inputs = {
            "query": user_msg,
            "topic": user_msg,
            "student_preferences": user_msg
        }

        # Run the workflow step
        result = crew.kickoff(inputs=inputs)

        # Detect if human feedback is required
        awaiting_feedback = False
        if "## HUMAN FEEDBACK" in str(result):
            awaiting_feedback = True

        return {
            "reply": str(result),
            "awaiting_feedback": awaiting_feedback,
            "conversation_id": conv_id
        }

    except Exception as e:
        print("Error executing crew:", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)