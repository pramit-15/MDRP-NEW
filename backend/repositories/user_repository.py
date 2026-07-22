from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.database.models.user import User
from backend.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_clerk_id(self, clerk_id: str) -> Optional[User]:
        stmt = select(User).where(User.clerk_id == clerk_id)
        return self.session.scalars(stmt).first()

    def get_or_create(self, clerk_id: str) -> User:
        user = self.get_by_clerk_id(clerk_id)
        if not user:
            user = self.create({"clerk_id": clerk_id})
        return user
