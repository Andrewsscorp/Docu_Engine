# i_security_services.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IHashService(ABC):
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass
        
    @abstractmethod
    def get_password_hash(self, password: str) -> str:
        pass

class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta_minutes: int) -> str:
        pass
