import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from graph.workflow import workflow
from dotenv import load_dotenv
import uuid
from core.memory import (
    create_conversation,
    get_conversations,
    get_conversation,
    rename_conversation,
    delete_conversation,
    add_message,
    get_conversation_context,
    extract_and_update_memory
)

load_dotenv()

# Compile the LangGraph
app_graph = workflow.compile()

app = FastAPI(title="Financial Advisor API", version="2.0")

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    title: Optional[str] = "New Chat"

class ConversationCreateRequest(BaseModel):
    title: Optional[str] = "New Chat"

class ConversationRenameRequest(BaseModel):
    title: str

@app.get("/")
def read_root():
    return {"status": "Financial Advisor API is running", "version": "2.0"}

# --- Conversation Endpoints ---

@app.get("/api/conversations")
def list_conversations():
    try:
        return get_conversations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
def new_conversation(request: Optional[ConversationCreateRequest] = None):
    try:
        title = request.title if request and request.title else "New Chat"
        conv_id = create_conversation(title=title)
        return {"id": conv_id, "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
def retrieve_conversation(conversation_id: str):
    try:
        conv = get_conversation(conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/conversations/{conversation_id}")
def update_conversation_title(conversation_id: str, request: ConversationRenameRequest):
    try:
        success = rename_conversation(conversation_id, request.title)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found or invalid title")
        return {"status": "success", "title": request.title}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
def remove_conversation(conversation_id: str):
    try:
        success = delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Chat Endpoint ---

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        query = request.message.strip()
        conv_id = request.conversation_id or str(uuid.uuid4())
        
        # Save user message
        add_message(conv_id, "user", query)
        
        # Retrieve context (structured facts + summary + recent turns) for this conversation
        memory_ctx = get_conversation_context(conv_id)
        
        # Prepare state for LangGraph
        initial_state = {
            "original_question": query,
            "current_question": query,
            "chat_history": [],
            "memory_context": memory_ctx,
            "conversation_id": conv_id
        }
        
        final_state = {}
        
        # Execute the LangGraph
        for out in app_graph.stream(initial_state):
            for node_name, state in out.items():
                final_state = state
                
        answer = final_state.get("final_answer") or final_state.get("draft_answer", "Sorry, I couldn't process your request.")
        
        # Save assistant message
        add_message(conv_id, "assistant", answer)
        
        # Extract facts, update conversation title if needed
        chat_title = extract_and_update_memory(conv_id, query, answer)
        
        return ChatResponse(
            answer=answer,
            conversation_id=conv_id,
            title=chat_title
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os
from fastapi.staticfiles import StaticFiles

# Serve built frontend in production if dist directory exists
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

