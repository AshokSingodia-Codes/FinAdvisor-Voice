import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import re
import json
import asyncio

from config.settings import settings
from graph.workflow import workflow
from dotenv import load_dotenv
import uuid
from core.memory import (
    create_conversation,
    get_conversations,
    get_conversation,
    get_conversation_raw,
    rename_conversation,
    delete_conversation,
    delete_all_conversations,
    add_message,
    get_conversation_context,
    extract_and_update_memory,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_password,
    save_otp_record,
    get_last_otp_record,
    verify_and_claim_otp,
    consume_verification_token,
    get_conversation_continuity,
    save_conversation_continuity
)
from core.auth import (
    hash_password,
    verify_password,
    generate_otp,
    hash_otp,
    send_otp_email,
    create_access_token,
    get_current_user,
    OTP_EXPIRY_MINUTES,
    OTP_RESEND_COOLDOWN_SECONDS
)
from core.rate_limiter import chat_rate_limiter
from core.cache import get_cached_response, set_cached_response, invalidate_document
from core.document_store import (
    ingest_document,
    delete_document,
    delete_documents_by_conversation,
    delete_all_documents_for_user,
    get_document_record,
    get_active_document_for_conversation,
    MAX_FILE_BYTES,
    NonFinancialDocumentError,
)
from tools.fast_math import try_evaluate_fast_math
from core.greeting_handler import is_greeting_or_chitchat, get_greeting_response

load_dotenv()



# Compile the LangGraph
app_graph = workflow.compile()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager — runs startup tasks and manages clean shutdown."""
    from core.regulatory_watcher import monthly_watchdog_background_loop
    # Start background workers
    reg_task = asyncio.create_task(monthly_watchdog_background_loop())
    snap_task = asyncio.create_task(_daily_snapshot_background_loop())
    # Pre-warm FlashRank, FastEmbed, Postgres, and Neo4j in background thread
    def _warmup():
        try:
            from retrieval.reranker import get_ranker
            get_ranker()
        except Exception as e:
            print(f"[Lifespan Warmup Notice] FlashRank warmup: {e}")

        try:
            from core.db import fast_embeddings
            fast_embeddings._get_model()
        except Exception as e:
            print(f"[Lifespan Warmup Notice] FastEmbed warmup: {e}")

        try:
            from core.memory import get_db_connection
            from sqlalchemy import text
            with get_db_connection() as conn:
                conn.execute(text("SELECT 1")).fetchone()
        except Exception as e:
            print(f"[Lifespan Warmup Notice] Postgres warmup: {e}")

        try:
            from core.db import kg
            kg.query("RETURN 1 AS val")
        except Exception as e:
            print(f"[Lifespan Warmup Notice] Neo4j warmup: {e}")

    asyncio.get_event_loop().run_in_executor(None, _warmup)
    yield  # application is running
    # Graceful shutdown — cancel background tasks
    reg_task.cancel()
    snap_task.cancel()


app = FastAPI(title="Financial Advisor API", version="2.0", lifespan=lifespan)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Request/Response Models ---

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def validate_email_format(email: str) -> str:
    cleaned = email.strip().lower()
    if not re.match(EMAIL_REGEX, cleaned):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    return cleaned

@app.get("/api/health")
def health_check():
    """Lightweight endpoint for health-ping cron jobs."""
    return {"status": "ok"}

class SendOtpRequest(BaseModel):
    email: str
    purpose: str = Field("register", description="Either 'register' or 'forgot_password'")

class VerifyOtpRequest(BaseModel):
    email: str
    otp: str
    purpose: str = Field("register", description="Either 'register' or 'forgot_password'")

class RegisterRequest(BaseModel):
    email: str
    password: str
    verification_token: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str
    verification_token: str

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []
    # When set, the retriever exclusively searches this personal document.
    # Must match a document uploaded to the same conversation_id by the same user.
    document_id: Optional[str] = None
    stream: Optional[bool] = False

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

# --- Authentication Endpoints ---

@app.post("/api/auth/send-otp")
def send_otp_endpoint(request: SendOtpRequest):
    email = validate_email_format(request.email)
    purpose = request.purpose.strip().lower()
    
    if purpose not in ["register", "forgot_password"]:
        raise HTTPException(status_code=400, detail="Invalid OTP purpose. Must be 'register' or 'forgot_password'.")
    
    existing_user = get_user_by_email(email)
    
    if purpose == "register" and existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please sign in.")
    
    if purpose == "forgot_password" and not existing_user:
        raise HTTPException(status_code=404, detail="No registered account found with this email.")
    
    # Check cooldown (60 seconds)
    last_otp = get_last_otp_record(email, purpose)
    if last_otp and last_otp.get("created_at"):
        try:
            created_dt = datetime.fromisoformat(last_otp["created_at"])
            if created_dt.tzinfo is None:
                created_dt = created_dt.replace(tzinfo=timezone.utc)
            now_dt = datetime.now(timezone.utc)
            elapsed = (now_dt - created_dt).total_seconds()
            if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
                remaining = int(OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(status_code=429, detail=f"Please wait {remaining} seconds before requesting a new OTP.")
        except HTTPException:
            raise
        except Exception:
            pass
    
    otp = generate_otp()
    otp_hash = hash_otp(otp)
    exp_iso = (datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
    
    save_otp_record(email, otp_hash, purpose, exp_iso)
    send_otp_email(email, otp, purpose)
    
    return {
        "status": "success",
        "message": f"OTP has been sent to {email}.",
        "cooldown_seconds": OTP_RESEND_COOLDOWN_SECONDS,
        "expires_in_minutes": OTP_EXPIRY_MINUTES
    }

@app.post("/api/auth/verify-otp")
def verify_otp_endpoint(request: VerifyOtpRequest):
    email = validate_email_format(request.email)
    otp_code = request.otp.strip()
    purpose = request.purpose.strip().lower()
    
    if not otp_code or len(otp_code) != 6:
        raise HTTPException(status_code=400, detail="Please enter a valid 6-digit OTP.")
    
    res = verify_and_claim_otp(email, otp_code, purpose)
    if not res["valid"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    
    return {
        "status": "success",
        "message": "OTP verified successfully.",
        "verification_token": res["verification_token"]
    }

@app.post("/api/auth/register")
def register_endpoint(request: RegisterRequest):
    email = validate_email_format(request.email)
    password = request.password
    vtoken = request.verification_token.strip()
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    
    # Validate and consume verification token
    valid_token = consume_verification_token(email, "register", vtoken)
    if not valid_token:
        raise HTTPException(status_code=400, detail="Invalid or expired verification session. Please verify your email again.")
    
    hashed_pwd = hash_password(password)
    user = create_user(email, hashed_pwd)
    
    return {
        "status": "success",
        "message": "Account created successfully! You can now sign in.",
        "user_id": user["id"]
    }

@app.post("/api/auth/login")
def login_endpoint(request: LoginRequest):
    email = validate_email_format(request.email)
    user = get_user_by_email(email)
    
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "created_at": user.get("created_at")
        }
    }

@app.post("/api/auth/forgot-password/reset")
def reset_password_endpoint(request: ResetPasswordRequest):
    email = validate_email_format(request.email)
    new_password = request.new_password
    vtoken = request.verification_token.strip()
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")
    
    valid_token = consume_verification_token(email, "forgot_password", vtoken)
    if not valid_token:
        raise HTTPException(status_code=400, detail="Invalid or expired verification session. Please verify OTP again.")
    
    new_hashed_pwd = hash_password(new_password)
    update_user_password(user["id"], new_hashed_pwd)
    
    return {
        "status": "success",
        "message": "Password updated successfully. You can now sign in with your new password."
    }

@app.get("/api/auth/me")
def get_me_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": current_user}

# --- Protected Conversation Endpoints ---

@app.get("/api/conversations")
def list_conversations(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        return get_conversations(user_id=current_user["id"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
def new_conversation(
    request: Optional[ConversationCreateRequest] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        title = request.title if request and request.title else "New Chat"
        conv_id = create_conversation(title=title, user_id=current_user["id"])
        return {"id": conv_id, "title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}")
def retrieve_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        raw = get_conversation_raw(conversation_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if raw["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied: You do not have permission to access this conversation.")
            
        conv = get_conversation(conversation_id, user_id=current_user["id"])
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/conversations/{conversation_id}")
def update_conversation_title(
    conversation_id: str,
    request: ConversationRenameRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        raw = get_conversation_raw(conversation_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if raw["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied: You do not have permission to rename this conversation.")
            
        success = rename_conversation(conversation_id, request.title, user_id=current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found or invalid title")
        return {"status": "success", "title": request.title}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations")
def remove_all_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        user_id = current_user["id"]
        delete_all_documents_for_user(user_id)
        delete_all_conversations(user_id)
        return {"status": "all_deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
def remove_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        raw = get_conversation_raw(conversation_id)
        if not raw:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if raw["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied: You do not have permission to delete this conversation.")
            
        delete_documents_by_conversation(conversation_id, user_id=current_user["id"])
        success = delete_conversation(conversation_id, user_id=current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Protected Chat Endpoints ---

@app.post("/api/chat")
async def chat_endpoint(
    request: ChatRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        query = request.message.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")
        user_id = current_user["id"]
        conv_id = request.conversation_id
        document_id = request.document_id or None
        is_stream_requested = request.stream or "text/event-stream" in http_request.headers.get("accept", "")

        # --- Rate limiting ---
        chat_rate_limiter.check_rate_limit(user_id)

        if conv_id:
            raw = get_conversation_raw(conv_id)
            if raw and raw["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You cannot send messages or access a conversation belonging to another user."
                )
            if not raw:
                create_conversation(title="New Chat", user_id=user_id, conversation_id=conv_id)
        else:
            conv_id = str(uuid.uuid4())
            create_conversation(title="New Chat", user_id=user_id, conversation_id=conv_id)

        # If document_id is not explicitly provided in the request, resolve the active document for this conversation
        if not document_id and conv_id:
            active_doc_rec = get_active_document_for_conversation(user_id=user_id, conversation_id=conv_id)
            if active_doc_rec:
                document_id = active_doc_rec["id"]

        # If a document_id is active, verify it belongs to this user AND this conversation
        if document_id:
            doc_record = get_document_record(document_id)
            if not doc_record:
                raise HTTPException(status_code=404, detail="Document not found.")
            if doc_record["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="Access denied: Document does not belong to you.")
            if doc_record["conversation_id"] != conv_id:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied: Document was uploaded to a different conversation. "
                           "Re-upload the document in the current conversation to use it here."
                )
            if doc_record["status"] != "ready":
                raise HTTPException(status_code=409, detail=f"Document is not ready (status: {doc_record['status']}).")

        # --- Deterministic Short-Circuit 1: Fast-Math Engine ---
        if not document_id:
            is_math, math_ans, _ = try_evaluate_fast_math(query)
            if is_math and math_ans:
                add_message(conv_id, "user", query, user_id=user_id)
                add_message(conv_id, "assistant", math_ans, user_id=user_id)
                set_cached_response(
                    question=query,
                    conversation_id=conv_id,
                    document_id=None,
                    answer=math_ans,
                    routing_decision="math_calculation",
                    user_id=user_id
                )
                background_tasks.add_task(extract_and_update_memory, conv_id, query, math_ans, user_id)
                chat_title = query[:35].title() if len(query) <= 35 else query[:30].title() + "..."
                if is_stream_requested:
                    async def event_generator():
                        yield f"event: step\ndata: {json.dumps({'node': 'fast_math'})}\n\n"
                        yield f"event: token\ndata: {json.dumps({'chunk': math_ans})}\n\n"
                        yield f"event: done\ndata: {json.dumps({'answer': math_ans, 'conversation_id': conv_id, 'title': chat_title})}\n\n"
                    return StreamingResponse(event_generator(), media_type="text/event-stream")
                return ChatResponse(answer=math_ans, conversation_id=conv_id, title=chat_title)

        # --- Deterministic Short-Circuit 2: Greetings & Chit-Chat ---
        if not document_id:
            is_greet, cat = is_greeting_or_chitchat(query)
            if is_greet and cat:
                prior_msgs = get_conversation_context(conv_id, user_id=user_id)
                turn_estimate = prior_msgs.count("[User]:")
                greet_ans = get_greeting_response(cat, query, turn_count=turn_estimate)
                add_message(conv_id, "user", query, user_id=user_id)
                add_message(conv_id, "assistant", greet_ans, user_id=user_id)
                set_cached_response(
                    question=query,
                    conversation_id=conv_id,
                    document_id=None,
                    answer=greet_ans,
                    routing_decision="direct_answer",
                    user_id=user_id
                )
                background_tasks.add_task(extract_and_update_memory, conv_id, query, greet_ans, user_id)
                chat_title = "Greeting"
                if is_stream_requested:
                    async def event_generator():
                        yield f"event: step\ndata: {json.dumps({'node': 'greeting_handler'})}\n\n"
                        yield f"event: token\ndata: {json.dumps({'chunk': greet_ans})}\n\n"
                        yield f"event: done\ndata: {json.dumps({'answer': greet_ans, 'conversation_id': conv_id, 'title': chat_title})}\n\n"
                    return StreamingResponse(event_generator(), media_type="text/event-stream")
                return ChatResponse(answer=greet_ans, conversation_id=conv_id, title=chat_title)

        # --- Cache check ---
        cached_answer = get_cached_response(
            question=query,
            conversation_id=conv_id,
            document_id=document_id,
            user_id=user_id,
        )
        if cached_answer:
            add_message(conv_id, "user", query, user_id=user_id)
            add_message(conv_id, "assistant", cached_answer, user_id=user_id)
            background_tasks.add_task(extract_and_update_memory, conv_id, query, cached_answer, user_id)
            chat_title = query[:35].title() if len(query) <= 35 else query[:30].title() + "..."
            if is_stream_requested:
                async def event_generator():
                    yield f"event: step\ndata: {json.dumps({'node': 'cache_hit'})}\n\n"
                    yield f"event: token\ndata: {json.dumps({'chunk': cached_answer})}\n\n"
                    yield f"event: done\ndata: {json.dumps({'answer': cached_answer, 'conversation_id': conv_id, 'title': chat_title})}\n\n"
                return StreamingResponse(event_generator(), media_type="text/event-stream")
            return ChatResponse(answer=cached_answer, conversation_id=conv_id, title=chat_title)

        # Save user message with user_id
        add_message(conv_id, "user", query, user_id=user_id)

        # Retrieve context with configurable windowing (default 6 turns)
        memory_ctx = get_conversation_context(conv_id, user_id=user_id, max_turns=settings.MAX_CHAT_HISTORY_TURNS)
        continuity = get_conversation_continuity(conv_id, user_id=user_id) if conv_id else {}
        active_entities = continuity.get("active_entities") or {}
        conversation_topic = continuity.get("conversation_topic") or ""

        # Prepare state for LangGraph with windowed history
        windowed_history = [
            m.model_dump() if hasattr(m, "model_dump") else m 
            for m in (request.chat_history or [])
        ][-settings.MAX_CHAT_HISTORY_TURNS:]

        initial_state = {
            "original_question": query,
            "current_question": query,
            "chat_history": windowed_history,
            "memory_context": memory_ctx,
            "conversation_id": conv_id,
            "user_id": user_id,
            "document_id": document_id,
            "active_entities": active_entities,
            "conversation_topic": conversation_topic,
        }

        if is_stream_requested:
            async def run_and_stream():
                final_state = {}
                # LangGraph node progress streaming
                for out in app_graph.stream(initial_state):
                    for node_name, state in out.items():
                        final_state = state
                        yield f"event: step\ndata: {json.dumps({'node': node_name})}\n\n"
                        await asyncio.sleep(0.01)

                ans = final_state.get("final_answer") or final_state.get("draft_answer", "Sorry, I couldn't process your request.")
                r_decision = final_state.get("routing_decision")
                set_cached_response(
                    question=query,
                    conversation_id=conv_id,
                    document_id=document_id,
                    answer=ans,
                    routing_decision=r_decision,
                    user_id=user_id,
                )
                add_message(conv_id, "assistant", ans, user_id=user_id)
                background_tasks.add_task(extract_and_update_memory, conv_id, query, ans, user_id)
                chat_title = query[:35].title() if len(query) <= 35 else query[:30].title() + "..."

                yield f"event: token\ndata: {json.dumps({'chunk': ans})}\n\n"
                yield f"event: done\ndata: {json.dumps({'answer': ans, 'conversation_id': conv_id, 'title': chat_title})}\n\n"

            return StreamingResponse(run_and_stream(), media_type="text/event-stream")

        final_state = {}
        # Execute standard LangGraph run
        for out in app_graph.stream(initial_state):
            for node_name, state in out.items():
                final_state = state

        answer = final_state.get("final_answer") or final_state.get("draft_answer", "Sorry, I couldn't process your request.")

        # --- Cache the response ---
        routing_decision = final_state.get("routing_decision")
        set_cached_response(
            question=query,
            conversation_id=conv_id,
            document_id=document_id,
            answer=answer,
            routing_decision=routing_decision,
            user_id=user_id,
        )

        # Save assistant message with user_id
        add_message(conv_id, "assistant", answer, user_id=user_id)

        # Offload fact extraction and title generation to background task
        background_tasks.add_task(extract_and_update_memory, conv_id, query, answer, user_id)
        chat_title = query[:35].title() if len(query) <= 35 else query[:30].title() + "..."

        return ChatResponse(
            answer=answer,
            conversation_id=conv_id,
            title=chat_title
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# --- Document Upload & Management Endpoints ---

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Upload a personal financial document and ingest it into Neo4j.

    The document is scoped to (user_id, document_id, conversation_id) — the
    same triple that every retrieval query filters on.  A document uploaded in
    Conversation A is invisible to Conversation B even for the same user.

    Limits: 5 MB, PDF / plain-text / markdown / CSV / Image (PNG, JPG, WEBP).
    """
    user_id = current_user["id"]

    # Verify the conversation belongs to this user
    raw = get_conversation_raw(conversation_id)
    if not raw:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    if raw["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Conversation does not belong to you.")

    # Read file content
    content = await file.read()

    # Size check (5 MB)
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is 5 MB ({MAX_FILE_BYTES:,} bytes). "
                   f"Your file is {len(content):,} bytes."
        )

    # MIME type check & normalizations with extension fallback
    mime_type = (file.content_type or "application/octet-stream").lower()
    filename = file.filename or "upload"
    filename_lower = filename.lower()

    if mime_type == "text/x-markdown" or filename_lower.endswith((".md", ".markdown")):
        mime_type = "text/markdown"
    elif filename_lower.endswith(".pdf"):
        mime_type = "application/pdf"
    elif filename_lower.endswith(".csv"):
        mime_type = "text/csv"
    elif filename_lower.endswith(".txt"):
        mime_type = "text/plain"
    elif filename_lower.endswith(".png"):
        mime_type = "image/png"
    elif filename_lower.endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif filename_lower.endswith(".webp"):
        mime_type = "image/webp"

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{mime_type}'. Allowed: PDF, plain text, markdown, CSV, and financial images (PNG, JPG, WEBP)."
        )

    try:
        record = ingest_document(
            content=content,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            conversation_id=conversation_id,
            background_tasks=background_tasks,
        )
        return {
            "status": "success",
            "document_id": record["id"],
            "filename": record["filename"],
            "chunk_count": record["chunk_count"],
            "file_size_bytes": record["file_size_bytes"],
            "conversation_id": conversation_id,
            "message": (
                f"Document '{filename}' ingested successfully ({record['chunk_count']} chunks). "
                "Pass document_id in subsequent chat requests to query it."
            )
        }
    except NonFinancialDocumentError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ValueError as e:
        # Size or MIME validation raised inside ingest_document
        raise HTTPException(status_code=413, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {e}")


@app.get("/api/documents/status/{document_id}")
def get_document_status(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    from core.document_store import get_document_record
    record = get_document_record(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    if record["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied.")
        
    return {
        "document_id": document_id,
        "status": record.get("status", "unknown"),
        "error_message": record.get("error_message"),
        "chunk_count": record.get("chunk_count", 0),
        "filename": record.get("filename"),
    }


@app.delete("/api/documents/{document_id}")
def delete_document_endpoint(
    document_id: str,
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Permanently delete a personal document and all its Neo4j chunks.

    The caller must be the document owner AND the conversation must match
    the conversation the document was originally uploaded to.
    Invalidates the cache for any answers derived from this document.
    """
    user_id = current_user["id"]

    doc_record = get_document_record(document_id)
    if not doc_record:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc_record["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Document does not belong to you.")
    if doc_record["conversation_id"] != conversation_id:
        raise HTTPException(status_code=403, detail="Access denied: Conversation ID mismatch.")

    deleted = delete_document(
        document_id=document_id,
        user_id=user_id,
        conversation_id=conversation_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found or already deleted.")

    # Evict any cached answers that were generated against this document
    invalidate_document(document_id)

    return {"status": "deleted", "document_id": document_id}

from core.regulatory_watcher import check_and_sync_financial_rules

# ─────────────────────────────────────────────────────────────────────────────
# Phase 6 — Daily Snapshot Scheduler
# Runs scripts/daily_snapshot_job.py every day at ~18:30 IST (13:00 UTC),
# capturing Indian equity closing prices and mutual fund NAVs into PostgreSQL.
# ─────────────────────────────────────────────────────────────────────────────

async def _daily_snapshot_background_loop():
    """
    Background async loop: runs run_daily_snapshots() once per day.
    Target time: 13:00 UTC (≈ 18:30 IST) — after NSE/BSE market close.
    On startup it sleeps until the next target window, then fires every 24h.
    """
    from datetime import datetime, timezone, timedelta
    import asyncio as _aio
    from scripts.daily_snapshot_job import run_daily_snapshots

    print("🕐 [Daily Snapshot Scheduler] Background worker initialized.")

    _TARGET_HOUR_UTC = 13  # 18:30 IST

    while True:
        try:
            now = datetime.now(timezone.utc)
            # Calculate seconds until next 13:00 UTC
            next_run = now.replace(hour=_TARGET_HOUR_UTC, minute=0, second=0, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)
            wait_secs = (next_run - now).total_seconds()
            print(f"  [Daily Snapshot Scheduler] Next run at {next_run.isoformat()}Z "
                  f"(in {wait_secs / 3600:.1f}h)")
            await _aio.sleep(wait_secs)

            # Execute the snapshot job in a thread-pool executor (blocking I/O)
            loop = _aio.get_event_loop()
            result = await loop.run_in_executor(None, run_daily_snapshots)
            print(f"  [Daily Snapshot Scheduler] Completed: "
                  f"equity+MF saved={result.get('success_count', 0)}, "
                  f"failed={result.get('fail_count', 0)}, "
                  f"mf_nav_saved={result.get('mf_nav_success', 0)}")
        except Exception as _exc:
            print(f"  [Daily Snapshot Scheduler Error]: {_exc}")
            # Back off 1 hour on error to prevent tight crash loops
            await _aio.sleep(3600)


# Startup/shutdown lifecycle is now managed by the lifespan() context manager above.
# (Migrated from deprecated @app.on_event("startup") to lifespan for FastAPI 0.100+ compatibility.)


@app.post("/api/admin/sync-regulatory-updates")
async def trigger_regulatory_sync(user_data: dict = Depends(get_current_user)):
    """Admin/Manual trigger to execute the monthly regulatory knowledge sync immediately."""
    result = check_and_sync_financial_rules()
    return result


@app.post("/api/admin/run-daily-snapshot")
async def trigger_daily_snapshot(user_data: dict = Depends(get_current_user)):
    """
    Admin/Manual trigger to execute the daily equity + mutual fund NAV snapshot job immediately.
    Useful for testing or catching up after a missed nightly run.
    """
    from scripts.daily_snapshot_job import run_daily_snapshots
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, run_daily_snapshots)
    return result


@app.get("/api/snapshots/{asset_type}/{symbol}")
async def get_snapshot_history(
    asset_type: str,
    symbol: str,
    limit: int = 30,
    user_data: dict = Depends(get_current_user)
):
    """
    Returns chronological daily price / NAV history for a tracked asset.

    - **asset_type**: `equity` or `mutual_fund`
    - **symbol**: NSE ticker (e.g. `RELIANCE.NS`) or AMFI scheme code (e.g. `122639`)
    - **limit**: number of historical records to return (default 30, max 365)
    """
    from core.memory import get_all_snapshots, get_historical_snapshot
    limit = min(max(1, limit), 365)
    records = get_all_snapshots(asset_type=asset_type, symbol_or_scheme_code=symbol, limit=limit)
    return {
        "asset_type": asset_type,
        "symbol": symbol,
        "count": len(records),
        "snapshots": records
    }


@app.get("/api/snapshots/{asset_type}/{symbol}/return")
async def get_snapshot_period_return(
    asset_type: str,
    symbol: str,
    current_value: float,
    period: str = "1w",
    user_data: dict = Depends(get_current_user)
):
    """
    Computes the percentage change for an asset over the requested period
    using stored daily snapshot history.

    - **asset_type**: `equity` or `mutual_fund`
    - **symbol**: ticker or AMFI scheme code
    - **current_value**: live price or NAV to compare against
    - **period**: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`
    """
    from tools.snapshot_helper import calculate_period_return
    result = calculate_period_return(
        asset_type=asset_type,
        symbol_or_scheme_code=symbol,
        current_value=current_value,
        period=period
    )
    return result


@app.get("/api/mf-nav/{scheme_code}")
async def get_mf_nav_history(
    scheme_code: str,
    target_date: Optional[str] = None,
    user_data: dict = Depends(get_current_user)
):
    """
    Returns the most recent NAV snapshot for an AMFI mutual fund scheme on or
    before the requested date (defaults to today).

    - **scheme_code**: AMFI scheme code (e.g. `122639` for Parag Parikh Flexi Cap)
    - **target_date**: ISO date string `YYYY-MM-DD` (optional, defaults to today)
    """
    from core.memory import get_historical_mf_nav
    from datetime import datetime, timezone
    if not target_date:
        target_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    record = get_historical_mf_nav(scheme_code=scheme_code, target_date=target_date)
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No NAV history found for scheme {scheme_code} on or before {target_date}."
        )
    return record

import os
from fastapi.staticfiles import StaticFiles

# Serve built frontend in production if dist directory exists
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

