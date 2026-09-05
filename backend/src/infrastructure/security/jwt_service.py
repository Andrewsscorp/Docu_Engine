# jwt_service.py
from datetime import datetime, timedelta
import os
import jwt
from typing import Dict, Any
from backend.src.domain.interfaces.i_security_services import ITokenService

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Missing SECRET_KEY environment variable")
if len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY must be at least 32 characters long")
ALGORITHM = "HS256"

class JWTTokenService(ITokenService):
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
