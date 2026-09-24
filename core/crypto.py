"""
core/crypto.py
--------------
Lightweight symmetric encryption utilities for user-uploaded document content.

Uses Fernet (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.
The encryption key must be set as ENCRYPTION_KEY in settings / .env.

If the key is absent (local dev without .env), a per-process ephemeral key
is generated with a warning so the app still starts.
"""

import os
import base64
from typing import Optional

_fernet = None


def _get_fernet():
    """Lazy-load Fernet to avoid import-time crashes if cryptography is missing."""
    global _fernet
    if _fernet is not None:
        return _fernet

    try:
        from cryptography.fernet import Fernet
    except ImportError:
        raise RuntimeError(
            "The 'cryptography' package is required for document encryption. "
            "Run: pip install cryptography"
        )

    raw_key = os.environ.get("ENCRYPTION_KEY", "").strip()

    if not raw_key:
        # Generate a fresh ephemeral key for this process.
        # Data encrypted with this key is lost on restart — only acceptable
        # for local development. Production MUST set ENCRYPTION_KEY in .env.
        generated = Fernet.generate_key()
        print(
            "[crypto] WARNING: ENCRYPTION_KEY not set. "
            "Using a per-process ephemeral key. "
            "Encrypted documents will be unreadable after restart. "
            "Set ENCRYPTION_KEY in .env for production."
        )
        _fernet = Fernet(generated)
    else:
        # Accept both raw base64url key strings and plain text passphrases.
        try:
            # Try to use it directly as a Fernet key (32 url-safe base64 bytes)
            _fernet = Fernet(raw_key.encode())
        except Exception:
            # Derive a valid 32-byte key from the passphrase using SHA-256
            import hashlib
            derived = base64.urlsafe_b64encode(
                hashlib.sha256(raw_key.encode()).digest()
            )
            _fernet = Fernet(derived)

    return _fernet


def encrypt_bytes(data: bytes) -> bytes:
    """
    Encrypt arbitrary bytes.

    Returns Fernet token bytes (base64url-encoded ciphertext + HMAC).
    Safe to store in a database or write to disk.
    """
    return _get_fernet().encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    """
    Decrypt a Fernet token back to the original bytes.

    Raises cryptography.fernet.InvalidToken if the token is tampered or
    was encrypted with a different key.
    """
    return _get_fernet().decrypt(token)


def encrypt_text(text: str, encoding: str = "utf-8") -> bytes:
    """Convenience wrapper: encrypt a string."""
    return encrypt_bytes(text.encode(encoding))


def decrypt_text(token: bytes, encoding: str = "utf-8") -> str:
    """Convenience wrapper: decrypt a Fernet token to a string."""
    return decrypt_bytes(token).decode(encoding)
