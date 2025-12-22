"""
Password Utility Module for Brain AI LMS
Provides secure password hashing and verification using bcrypt
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import jwt, JWTError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
    
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: The plain text password to hash
    
    Returns:
        str: The hashed password
    """
    try:
        hashed = pwd_context.hash(password)
        return hashed
    except Exception as e:
        logger.error(f"Password hashing error: {e}")
        raise ValueError("Failed to hash password")


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        logger.error(f"JWT encoding error: {e}")
        raise ValueError("Failed to create access token")


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: The payload data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        str: The encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        logger.error(f"JWT refresh token encoding error: {e}")
        raise ValueError("Failed to create refresh token")


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token
    
    Args:
        token: The JWT token to decode
    
    Returns:
        dict: The decoded token payload
    
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decoding error: {e}")
        raise


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token
    
    Args:
        email: The user's email address
    
    Returns:
        str: The password reset token
    """
    expires = timedelta(hours=1)
    token = create_access_token(
        data={"sub": email, "type": "password_reset"},
        expires_delta=expires
    )
    return token


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return the email
    
    Args:
        token: The password reset token
    
    Returns:
        Optional[str]: The email if token is valid, None otherwise
    """
    try:
        payload = decode_token(token)
        if payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except JWTError:
        return None


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    
    Args:
        password: The password to validate
    
    Returns:
        dict: Validation result with is_valid and errors
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one number")
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for char in password):
        errors.append("Password must contain at least one special character")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def hash_password_with_salt(password: str, salt: str) -> str:
    """
    Hash a password with a custom salt (for specific use cases)
    
    Args:
        password: The plain text password
        salt: The salt to use for hashing
    
    Returns:
        str: The hashed password with salt
    """
    salted_password = password + salt
    return get_password_hash(salted_password)


class TokenPayload:
    """Token payload structure"""
    def __init__(
        self,
        user_id: int,
        email: str,
        role: str,
        exp: datetime,
        iat: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.exp = exp
        self.iat = iat


def extract_token_payload(token: str) -> TokenPayload:
    """
    Extract and validate token payload into a structured object
    
    Args:
        token: The JWT token
    
    Returns:
        TokenPayload: The structured token payload
    """
    payload = decode_token(token)
    
    return TokenPayload(
        user_id=int(payload.get("sub", 0)),
        email=payload.get("email", ""),
        role=payload.get("role", "student"),
        exp=datetime.fromtimestamp(payload.get("exp", 0)),
        iat=datetime.fromtimestamp(payload.get("iat", 0)) if payload.get("iat") else None
    )


if __name__ == "__main__":
    # Demo usage
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    print(f"Original: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verified: {verify_password(password, hashed)}")
    
    # Token demo
    token_data = {"sub": "1", "email": "user@example.com", "role": "student"}
    access_token = create_access_token(token_data)
    print(f"\nAccess Token: {access_token[:50]}...")
    
    # Password strength validation
    result = validate_password_strength("weak")
    print(f"\nPassword 'weak' validation: {result}")
    
    result = validate_password_strength("StrongPass123!")
    print(f"Password 'StrongPass123!' validation: {result}")
