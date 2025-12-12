<script setup>
import { ref, nextTick, onMounted } from "vue";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/api/chat";

// --- STATE ---
const userInput = ref("");
const messages = ref([
  {
    role: "bot",
    content:
      "👋 Hi there! I am your Erasmus Planner AI.\n\nTell me where you want to go or ask about your Learning Agreement."
  }
]);
const isLoading = ref(false);
const chatContainer = ref(null);
const conversationId = ref(null);

// --- SCROLL ---
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTo({
      top: chatContainer.value.scrollHeight,
      behavior: "smooth"
    });
  }
};

onMounted(scrollToBottom);

// --- SEND MESSAGE ---
const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const userMsg = userInput.value;
  messages.value.push({ role: "user", content: userMsg });
  userInput.value = "";
  isLoading.value = true;
  scrollToBottom();

  try {
    const response = await axios.post(API_URL, {
      message: userMsg,
      conversation_id: conversationId.value
    });

    const botReply = response.data.reply || "⚠️ No reply received.";
    messages.value.push({ role: "bot", content: botReply });

    // Store conversation id
    conversationId.value = response.data.conversation_id;

    // If awaiting human feedback, keep input enabled
    if (response.data.awaiting_feedback) {
      console.log("⚠️ Bot is awaiting your feedback. Type your reply to continue.");
    }

  } catch (err) {
    console.error("Backend error:", err);
    messages.value.push({
      role: "bot",
      content: "⚠️ Error connecting to backend."
    });
  }

  isLoading.value = false;
  scrollToBottom();
};
</script>

<template>
  <div class="main-container">
    <div class="chat-card">
      <div class="chat-header">
        <div class="header-content">
          <h1>Erasmus Planner</h1>
        </div>
      </div>

      <div class="messages-container" ref="chatContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message-wrapper', msg.role === 'user' ? 'user-wrapper' : 'bot-wrapper']"
        >
           <div class="avatar bot-avatar" v-if="msg.role === 'bot'">🤖</div>

          <div :class="['message-bubble', msg.role === 'user' ? 'user-msg' : 'bot-msg']">
            <div class="message-text" :style="{ whiteSpace: 'pre-wrap' }">{{ msg.content }}</div>
             
          </div>
        </div>

        <div v-if="isLoading" class="message-wrapper bot-wrapper loading-wrapper">
           <div class="avatar bot-avatar">🤖</div>
          <div class="message-bubble bot-msg loading-bubble">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-container">
        <div class="input-wrapper">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage"
            placeholder="Type your questions here..." 
            type="text" 
            :disabled="isLoading"
          />
          <button @click="sendMessage" :disabled="isLoading || !userInput.trim()" class="send-btn">
            Send
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Define our purplish theme colors */
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Vibrant Purple/Blue */
  --secondary-purple: #f3f0ff; /* Light lavender background for bot */
  --dark-text: #2d3748;
  --light-text: #ffffff;
  --shadow-soft: 0 10px 30px -10px rgba(0, 0, 0, 0.15);
  --shadow-input: 0 -5px 20px -5px rgba(0,0,0,0.05);
}

/* The container that centers the card on the screen */
.main-container {
  width: 100%;
  height: 95vh; /* Takes up most of the screen height */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
}

/* The main chat card */
.chat-card {
  width: 100%;
  max-width: 80vw; /* A bit narrower for a modern phone-like feel */
  height: 100%;
  max-height: 800px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* === Header === */
.chat-header {
  background: var(--primary-gradient);
  padding: 20px;
  text-align: center;
  color: var(--light-text);
  box-shadow: 0 4px 15px -5px rgba(118, 75, 162, 0.4);
  z-index: 10;
}

.header-content h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.header-content p {
  margin: 5px 0 0 0;
  font-size: 0.9rem;
  opacity: 0.9;
}

/* === Messages Area === */
.messages-container {
  flex: 1;
  padding: 20px 15px;
  overflow-y: auto;
  background-color: #fafafa; /* Very light grey background for contrast */
  background-image: radial-gradient(#eaeaea 1px, transparent 1px);
  background-size: 20px 20px; /* Subtle dot pattern */
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Hide scrollbar for cleaner look (Chrome/Safari/Webkit) */
.messages-container::-webkit-scrollbar {
    width: 6px;
}
.messages-container::-webkit-scrollbar-thumb {
    background-color: rgba(118, 75, 162, 0.2);
    border-radius: 10px;
}

/* Wrappers hold the bubble and potential avatars */
.message-wrapper {
  display: flex;
  align-items: flex-end;
  margin-bottom: 10px;
  animation: fadeIn 0.3s ease-out;
}

.bot-wrapper {
   justify-content: flex-start;
}

.user-wrapper {
   justify-content: flex-end;
}

.avatar {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    font-size: 1.2rem;
    margin-bottom: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.bot-avatar { 
    background: white; 
    margin-right: 8px; 
    color: #764ba2;
}

.user-avatar { 
    background: var(--primary-gradient); 
    margin-left: 8px; 
    color: white;
    font-size: 1rem;
}

/* The actual colored bubbles */
.message-bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 20px;
  font-size: 0.95rem;
  line-height: 1.5;
  position: relative;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
}

.bot-msg {
  background-color: var(--secondary-purple);
  color: var(--dark-text);
  border-bottom-left-radius: 4px; /* Little tail effect */
}

.user-msg {
  background: #d9c6ff71; /* soft lavender purple */
  color: var(--dark-text);
  border-bottom-right-radius: 4px;
}


/* === Input Area === */
.input-container {
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.9); /* Slightly transparent */
  backdrop-filter: blur(10px); /* Glassmorphism effect */
  border-top: 1px solid rgba(0,0,0,0.05);
  box-shadow: var(--shadow-input);
  z-index: 10;
}

.input-wrapper {
  display: flex;
  background: #f4f7f9;
  border-radius: 30px;
  padding: 5px 5px 5px 20px; /* Padding room for the button */
  align-items: center;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

/* Highlights the whole input bar when typing */
.input-wrapper:focus-within {
    border-color: #a485d6;
    background: white;
    box-shadow: 0 4px 15px rgba(118, 75, 162, 0.15);
}

input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 1rem;
  color: var(--dark-text);
  padding: 10px 0;

  /* Prevent overflow */
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
}


input::placeholder {
    color: #aaa;
}

/* The simplified Send button */
/* The Simple Send Button */
.send-btn {
  /* Using the Teal from your palette */
  background-color: #764ba2; 
  color: white;
  
  /* Reset generic button styles */
  border: none;
  outline: none;
  
  /* Sizing */
  padding: 0 24px;
  height: 42px; /* Match input height */
  border-radius: 21px;
  
  /* Text styling */
  font-weight: 600;
  font-size: 0.95rem;
  font-family: inherit;
  
  /* Positioning */
  cursor: pointer;
  margin-left: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  /* Animation setup */
  transition: all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  box-shadow: 0 4px 12px rgba(66, 182, 198, 0.3); /* Teal shadow */
}

/* Hover State (Lift up) */
.send-btn:hover:not(:disabled) {
  background-color: #667eea; /* Slightly darker teal */
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(66, 182, 198, 0.4);
}

/* Click State (Press down) */
.send-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 5px rgba(66, 182, 198, 0.3);
}

/* Disabled State */
.send-btn:disabled {
  background-color: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* === Animations === */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Modern typing indicator dots */
.typing-indicator {
  display: flex;
  align-items: center;
  height: 24px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #a485d6;
  border-radius: 50%;
  display: inline-block;
  margin: 0 3px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}
</style>