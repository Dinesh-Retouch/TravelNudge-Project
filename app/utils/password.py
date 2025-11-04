from passlib.context import CryptContext
import hashlib

# Use a different hashing algorithm that doesn't have the 72-byte limit
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt", "django_pbkdf2_sha256"],
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    """Hash a password using the available schemes"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)