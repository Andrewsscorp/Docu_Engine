# jwt_service.py
from datetime import datetime, timedelta
import jwt
from typing import Dict, Any
from backend.src.domain.interfaces.i_security_services import ITokenService

SECRET_KEY = "super_secret_key_for_testing" # Debería venir de env vars
ALGORITHM = "HS256"

class JWTTokenService(ITokenService):
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
