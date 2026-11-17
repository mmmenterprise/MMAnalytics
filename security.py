import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from cryptography.fernet import Fernet
from database import settings
import base64
import hashlib

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_long_term_token(user_id: str) -> str:
    """Generate a random long-term API key and return the plain version.
    Caller must store the hash."""
    return secrets.token_urlsafe(48)

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_onboarding_token() -> str:
    return secrets.token_urlsafe(32)

# Encryption for Claude keys
def get_fernet() -> Fernet:
    # Derive a proper Fernet key from the settings string
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.encryption_key.encode()).digest())
    return Fernet(key)

def encrypt_claude_key(plain_key: str) -> str:
    if not plain_key:
        return None
    return get_fernet().encrypt(plain_key.encode()).decode()

def decrypt_claude_key(encrypted: str) -> str:
    if not encrypted:
        return None
    return get_fernet().decrypt(encrypted.encode()).decode()
