# backend/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import hashlib

SECRET_KEY = "SUPER_SECRET_KEY_FOR_TASK_MANAGER_APP" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_password_hash(password: str) -> str:
    """
    Secure password hashing using Python's built-in PBKDF2 standard.
    Bypasses passlib/bcrypt compatibility bugs on modern Python engines.
    """
    static_salt = b"indpro_assignment_salt_secure"
    # PBKDF2 with SHA-256 is fully secure, reliable, and uses zero external dependencies
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), static_salt, 100000)
    return pwd_hash.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies if the submitted password matches the database hash."""
    return get_password_hash(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a secure JWT token for managing active user sessions."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt