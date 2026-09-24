import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import re

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
    consume_verification_token
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
    get_document_record,
    get_active_document_for_conversation,
    MAX_FILE_BYTES,
    NonFinancialDocumentError,
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

# --- Pydantic Request/Response Models ---

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def validate_email_format(email: str) -> str:
    cleaned = email.strip().lower()
    if not re.match(EMAIL_REGEX, cleaned):
        raise HTTPException(status_code=400, detail="Invalid email address format.")
    return cleaned

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
            
        success = delete_conversation(conversation_id, user_id=current_user["id"])
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Protected Chat Endpoint ---

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        query = request.message.strip()
        user_id = current_user["id"]
        conv_id = request.conversation_id
        document_id = request.document_id or None

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

        # --- Cache check (skip for live market queries) ---
        cached_answer = get_cached_response(
            question=query,
            conversation_id=conv_id,
            document_id=document_id,
        )
        if cached_answer:
            add_message(conv_id, "user", query, user_id=user_id)
            add_message(conv_id, "assistant", cached_answer, user_id=user_id)
            chat_title = extract_and_update_memory(conv_id, query, cached_answer, user_id=user_id)
            return ChatResponse(answer=cached_answer, conversation_id=conv_id, title=chat_title)

        # Save user message with user_id
        add_message(conv_id, "user", query, user_id=user_id)

        # Retrieve context (structured facts + summary + recent turns) for this conversation
        memory_ctx = get_conversation_context(conv_id, user_id=user_id)

        # Prepare state for LangGraph
        initial_state = {
            "original_question": query,
            "current_question": query,
            "chat_history": [],
            "memory_context": memory_ctx,
            "conversation_id": conv_id,
            "user_id": user_id,
            "document_id": document_id,
        }

        final_state = {}

        # Execute the LangGraph
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
        )

        # Save assistant message with user_id
        add_message(conv_id, "assistant", answer, user_id=user_id)

        # Extract facts, update conversation title if needed
        chat_title = extract_and_update_memory(conv_id, query, answer, user_id=user_id)

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
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Upload a personal financial document and ingest it into Neo4j.

    The document is scoped to (user_id, document_id, conversation_id) — the
    same triple that every retrieval query filters on.  A document uploaded in
    Conversation A is invisible to Conversation B even for the same user.

    Limits: 10 MB, PDF / plain-text / markdown / CSV / Image (PNG, JPG, WEBP).
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

    # Size check (10 MB)
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is 10 MB ({MAX_FILE_BYTES:,} bytes). "
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

from core.regulatory_watcher import check_and_sync_financial_rules, monthly_watchdog_background_loop
import asyncio

@app.on_event("startup")
async def startup_event():
    # Start the monthly regulatory watchdog in the background
    asyncio.create_task(monthly_watchdog_background_loop())
    # Pre-warm FlashRank ranker and FastEmbed in background to eliminate query cold-starts
    def _warmup():
        try:
            from retrieval.reranker import get_ranker
            get_ranker()
        except Exception:
            pass
    asyncio.get_event_loop().run_in_executor(None, _warmup)

@app.post("/api/admin/sync-regulatory-updates")
async def trigger_regulatory_sync(user_data: dict = Depends(get_current_user)):
    """Admin/Manual trigger to execute the monthly regulatory knowledge sync immediately."""
    result = check_and_sync_financial_rules()
    return result

import os
from fastapi.staticfiles import StaticFiles

# Serve built frontend in production if dist directory exists
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

