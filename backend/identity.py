import secrets
from abc import ABC, abstractmethod

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Enrollment, User


class IdentityProvider(ABC):
    @abstractmethod
    def login(self, user: User) -> str:
        pass

    @abstractmethod
    def logout(self, token: str):
        pass

    @abstractmethod
    def get_current_user(self, token: str, db: Session) -> User | None:
        pass

    @abstractmethod
    def is_enrolled(self, user: User, course_id: int, db: Session) -> Enrollment | None:
        pass


class DemoIdentityProvider(IdentityProvider):
    def __init__(self):
        self.sessions: dict[str, int] = {}

    def login(self, user: User) -> str:
        token = secrets.token_urlsafe(32)
        self.sessions[token] = user.id
        return token

    def logout(self, token: str):
        self.sessions.pop(token, None)

    def get_current_user(self, token: str, db: Session) -> User | None:
        user_id = self.sessions.get(token)
        return db.get(User, user_id) if user_id is not None else None

    def is_enrolled(self, user: User, course_id: int, db: Session) -> Enrollment | None:
        return db.scalar(select(Enrollment).where(Enrollment.user_id == user.id, Enrollment.course_id == course_id))


provider: IdentityProvider = DemoIdentityProvider()
bearer = HTTPBearer(auto_error=False)


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    user = provider.get_current_user(credentials.credentials, db) if credentials else None
    if user is None:
        raise HTTPException(status_code=401, detail='Oturum açmanız gerekiyor.')
    return user


def require_enrollment(user: User, course_id: int, db: Session, role: str | None = None):
    enrollment = provider.is_enrolled(user, course_id, db)
    if enrollment is None or (role and enrollment.role != role):
        raise HTTPException(status_code=403, detail='Bu işlem için yetkiniz yok.')
    return enrollment
