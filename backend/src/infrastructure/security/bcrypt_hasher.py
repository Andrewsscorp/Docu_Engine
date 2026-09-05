# bcrypt_hasher.py
from passlib.context import CryptContext
from backend.src.domain.interfaces.i_security_services import IHashService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptHashService(IHashService):
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
