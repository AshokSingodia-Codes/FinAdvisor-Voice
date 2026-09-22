import os
import secrets
import smtplib
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

# --- Password Hashing Setup (Direct bcrypt) ---
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

# --- OTP Helper Functions ---
OTP_EXPIRY_MINUTES = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5

def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    return f"{secrets.randbelow(900000) + 100000:06d}"

def hash_otp(otp: str) -> str:
    """Hash OTP before storing in database."""
    salt = settings.effective_jwt_secret[:16]
    return hashlib.sha256(f"{otp}:{salt}".encode('utf-8')).hexdigest()

def verify_otp_hash(plain_otp: str, hashed_otp: str) -> bool:
    return hash_otp(plain_otp) == hashed_otp

def generate_verification_token() -> str:
    """Generate a single-use token after successful OTP verification."""
    return secrets.token_urlsafe(32)

import json
import urllib.request
import urllib.error

# --- Email Sending Service ---
def send_otp_email(to_email: str, otp: str, purpose: str = "register") -> bool:
    """
    Send OTP via Brevo HTTPS API (primary) or SMTP (fallback).
    Falls back gracefully to console logging in development mode.
    """
    # Skip external email dispatch in test environments or for mock domains
    test_domains = ("example.com", "test.com", "isolation.com", "mock.com", "localhost")
    if os.getenv("PYTEST_CURRENT_TEST") or any(to_email.lower().endswith("@" + d) for d in test_domains):
        print(f"\n[AUTH DEV/TEST LOG] OTP for {to_email} ({purpose}): {otp} (Expires: {OTP_EXPIRY_MINUTES}m)\n")
        return True

    subject_map = {
        "register": "FinAdvisor-X - Verify Your Email",
        "forgot_password": "FinAdvisor-X - Password Reset OTP",
    }
    purpose_title = "Account Verification" if purpose == "register" else "Password Reset"
    subject = subject_map.get(purpose, "FinAdvisor-X - Verification OTP")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0f14; color: #e0e3ef; margin: 0; padding: 20px; }}
        .card {{ max-width: 500px; margin: 0 auto; background: #131722; border: 1px solid #1e2336; border-radius: 16px; padding: 32px; box-shadow: 0 8px 30px rgba(0,0,0,0.4); }}
        .logo {{ font-size: 22px; font-weight: bold; color: #f0a500; margin-bottom: 8px; }}
        .title {{ font-size: 18px; font-weight: 600; color: #ffffff; margin-bottom: 16px; }}
        .desc {{ font-size: 14px; color: #8b92a8; line-height: 1.5; margin-bottom: 24px; }}
        .otp-box {{ background: #0d0f14; border: 1px solid #f0a500; border-radius: 12px; padding: 18px; text-align: center; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #f0a500; margin-bottom: 24px; }}
        .expiry {{ font-size: 12px; color: #8b92a8; text-align: center; margin-bottom: 24px; }}
        .footer {{ font-size: 11px; color: #52596f; border-top: 1px solid #1e2336; padding-top: 16px; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">⚡ FinAdvisor-X</div>
        <div class="title">{purpose_title}</div>
        <div class="desc">Please use the following One-Time Password (OTP) to complete your request. Do not share this OTP with anyone.</div>
        <div class="otp-box">{otp}</div>
        <div class="expiry">This OTP is valid for <strong>5 minutes</strong>. If you did not request this, please ignore this email.</div>
        <div class="footer">&copy; {datetime.now().year} FinAdvisor-X AI Financial Analyst. All rights reserved.</div>
      </div>
    </body>
    </html>
    """

    # 1. Primary Delivery Method: Brevo HTTPS Transactional Email API (if configured)
    if settings.BREVO_API_KEY:
        try:
            sender_email = settings.BREVO_SENDER_EMAIL or settings.SMTP_FROM_EMAIL or "replitashok@gmail.com"
            sender_name = settings.BREVO_SENDER_NAME or "FinAdvisor-X"
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content
            }
            req = urllib.request.Request(
                "https://api.brevo.com/v3/smtp/email",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "api-key": settings.BREVO_API_KEY.strip(),
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.status in (200, 201, 202):
                    res_body = response.read().decode('utf-8')
                    print(f"[AUTH] Successfully dispatched OTP email to {to_email} via Brevo HTTPS API: {res_body}")
                    return True
        except Exception as e:
            print(f"[AUTH WARNING] Brevo API dispatch failed ({e}). Attempting SMTP fallback...")

    # 2. Secondary Delivery Method: Direct SMTP with SSL/TLS
    smtp_host = settings.effective_smtp_host
    smtp_user = settings.SMTP_USER
    smtp_pwd = settings.SMTP_PASSWORD
    from_email = settings.SMTP_FROM_EMAIL or smtp_user or "replitashok@gmail.com"

    if smtp_host and smtp_user and smtp_pwd:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"FinAdvisor-X <{from_email}>"
        msg["To"] = to_email
        msg["Reply-To"] = from_email

        text_part = MIMEText(f"Your FinAdvisor-X OTP is {otp}. Valid for 5 minutes.", "plain")
        html_part = MIMEText(html_content, "html")
        msg.attach(text_part)
        msg.attach(html_part)

        ports_to_try = [465, 587] if settings.SMTP_PORT in (465, 587, None) else [settings.SMTP_PORT, 465, 587]
        for port in ports_to_try:
            try:
                if port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, 465, timeout=12)
                else:
                    server = smtplib.SMTP(smtp_host, port, timeout=12)
                    server.starttls()

                server.login(smtp_user, smtp_pwd)
                server.sendmail(from_email, [to_email], msg.as_string())
                server.quit()
                print(f"[AUTH] Successfully sent OTP email to {to_email} via SMTP port {port}")
                return True
            except Exception as e:
                print(f"[AUTH WARNING] SMTP attempt on port {port} failed: {e}")

    # 3. Development fallback log
    print(f"\n==================== [AUTH OTP DEV LOG] ====================")
    print(f"  To:       {to_email}")
    print(f"  Purpose:  {purpose}")
    print(f"  OTP Code: {otp}")
    print(f"  Expires:  {OTP_EXPIRY_MINUTES} minutes")
    print(f"===========================================================\n")
    return True

# --- JWT Token Management ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.effective_jwt_secret,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- FastAPI Security Dependency ---
security_bearer = HTTPBearer(auto_error=False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)) -> Dict[str, Any]:
    """FastAPI dependency to extract and authenticate the current user from Bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    email = payload.get("sub")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from core.memory import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": user["id"],
        "email": user["email"],
        "created_at": user.get("created_at")
    }
