# i_user_repository.py
from typing import Optional
from abc import ABC, abstractmethod
from backend.src.domain.entities.usuario import Usuario

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        pass
