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
    def import_students(self, students: list[dict[str, str]], course_id: int, db: Session) -> dict[str, int]:
        pass

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

    def import_students(self, students: list[dict[str, str]], course_id: int, db: Session) -> dict[str, int]:
        created = enrolled = 0
        for student in students:
            by_number = db.scalar(select(User).where(User.student_number == student['student_number']))
            by_email = db.scalar(select(User).where(User.email == student['email']))
            if (by_number and (by_number.email != student['email'] or by_number.role != 'student')) or (by_email and by_email != by_number):
                raise HTTPException(409, 'Öğrenci numarası veya e-posta mevcut bir kullanıcıyla uyuşmuyor.')
            user = by_number
            if user is None:
                user = User(**student, role='student')
                db.add(user)
                db.flush()
                created += 1
            if self.is_enrolled(user, course_id, db) is None:
                db.add(Enrollment(user_id=user.id, course_id=course_id, role='student'))
                enrolled += 1
        db.commit()
        return {'created': created, 'enrolled': enrolled}

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
