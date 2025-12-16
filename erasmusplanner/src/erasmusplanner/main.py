import os
import threading
from dotenv import load_dotenv
import panel as pn

load_dotenv()
pn.extension(
    design="material",
    raw_css=[ """
/* =====================================================
   ERASMUS CHAT - FIXED LAYOUT
===================================================== */

:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --bot-bg: #f3f0ff;
  --user-bg: #d9c6ff71;
  --dark-text: #2d3748;
}

/* ---------- BACKGROUND ---------- */
body {
  margin: 0;
  padding: 0;
  background-color: #4c1d95;
  background-image:
    radial-gradient(at 0% 0%, #e879f9 0px, transparent 50%),
    radial-gradient(at 100% 100%, #4c1d95 0px, transparent 50%);
  font-family: Inter, system-ui, sans-serif;
  
  /* 🚨 FORCE CENTER ALIGNMENT */
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100vw;
  overflow: hidden; 
}

/* ---------- THE CARD (FIXED HEIGHT) ---------- */
.floating-card {
  height: 85vh !important;       /* 🚨 HARD LIMIT: 85% of screen height */
  width: 900px !important;       /* Fixed width */
  max-width: 95vw !important;    /* Responsive for small screens */
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
  
  display: flex;
  flex-direction: column;
  overflow: hidden;              /* Clips anything sticking out */
}

/* ---------- CHAT INTERFACE WRAPPER ---------- */
.bk-chat-interface {
  display: flex;
  flex-direction: column;
  height: 100% !important;       /* Fill the card */
  width: 100% !important;
}

/* ---------- MESSAGES (SCROLLABLE AREA) ---------- */
.bk-chat-messages {
  flex-grow: 1;                  /* Takes all available space */
  overflow-y: auto;              /* SCROLLS here */
  min-height: 0;                 /* 🚨 CRITICAL: Allows shrinking */
  padding: 20px;
}

/* ---------- INPUT BAR (FIXED BOTTOM) ---------- */
.bk-chat-input {
  flex-shrink: 0;                /* Never shrink this */
  padding: 15px 20px 20px 20px;  /* Comfy padding */
  border-top: 1px solid rgba(0,0,0,0.1);
  background: white;
  z-index: 10;
}

/* ---------- STYLING EXTRAS ---------- */
.bk-chat-message {
  padding: 12px 16px;
  border-radius: 18px;
  margin-bottom: 8px;
  max-width: 80%;
}
.bk-chat-message.assistant { background: var(--bot-bg); color: var(--dark-text); }
.bk-chat-message.user { background: var(--user-bg); color: var(--dark-text); }

/* Hide scrollbar track but show handle */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
""" ]
)

from erasmusplanner.crew import Erasmusplanner
from erasmusplanner.crew import chat_interface
from erasmusplanner.ui_state import set_user_input

# ---------------------------------------------------------------------
# LOGIC
# ---------------------------------------------------------------------

crew_running = False



def initiate_chat(message: str):
    global crew_running
    crew_running = True
    try:
        crew = Erasmusplanner().crew()
        crew.kickoff(inputs={"topic": message})
    except Exception as e:
        chat_interface.send(f"Error: {e}", user="System", respond=False)
    finally:
        crew_running = False

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    global crew_running
    if not crew_running:
        thread = threading.Thread(target=initiate_chat, args=(contents,), daemon=True)
        thread.start()
    else:
        set_user_input(contents)

chat_interface.callback = callback

chat_interface.send(
    "Welcome! I'm your Erasmus Assistant.Chat with me and let's get started with you Learning Agreement!",
    user="Assistant", respond=False
)

# ---------------------------------------------------------------------
# LAYOUT (THE FIX)
# ---------------------------------------------------------------------

# We wrap the chat interface in a plain Column and apply the CSS class
card = pn.Column(
    chat_interface,
    css_classes=["floating-card"], 
    margin=0
)

# Serve it. explicit CSS handles the centering on 'body'
card.servable()