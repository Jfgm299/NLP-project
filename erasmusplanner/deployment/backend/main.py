import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# === 1. PATH SETUP ===
# We need to add the project root to sys.path so Python can find 'src'
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../deployment/backend
project_root = os.path.abspath(os.path.join(current_dir, "../../")) # .../
sys.path.append(project_root)

# === 2. IMPORT YOUR CREW ===
# Now we can import the class from src/erasmusplanner/crew.py
# Make sure your __init__.py files exist if you get import errors, 
# but usually sys.path fix is enough.
from src.erasmusplanner.crew import Erasmusplanner

load_dotenv()

app = FastAPI()

# === 3. CORS CONFIG ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow your Vue app
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def run_chat(request: ChatRequest):
    try:
        print(f"Received query: {request.message}")

        # === 4. PREPARE INPUTS ===
        # Your tasks.yaml likely uses variables like {topic} or {query}.
        # We map the user's message to a generic 'query' or 'topic' key.
        # Adjust these keys to match what is inside your src/erasmusplanner/config/tasks.yaml
        inputs = {
            'topic': request.message,
            'query': request.message,
            'student_preferences': request.message 
        }

        # === 5. RUN THE CREW ===
        # We instantiate the class and call .crew() to get the Crew object
        # Then we kickoff with the inputs
        erasmus_crew = Erasmusplanner()
        result = erasmus_crew.crew().kickoff(inputs=inputs)

        # === 6. RETURN RESULT ===
        # CrewAI returns a 'CrewOutput' object, we convert it to string/markdown
        return {"reply": str(result)}

    except Exception as e:
        print(f"Error executing crew: {e}")
        # Detailed error for debugging
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Using 127.0.0.1 for local dev
    uvicorn.run(app, host="127.0.0.1", port=8000)