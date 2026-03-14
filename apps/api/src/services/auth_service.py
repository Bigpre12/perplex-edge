import os
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "perplex_ultra_secret_fallback_key_99")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200)) # Default 30 days

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against the hashed version."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate a bcrypt hash of the password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        # Note: 'tier' should be passed in 'data' from the router
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt


    def decode_access_token(self, token: str) -> dict:
        """Decode and validate a JWT access token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.JWTError:
            return None

auth_service = AuthService()
