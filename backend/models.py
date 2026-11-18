from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    recording_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Course(Base):
    __tablename__ = 'courses'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))


class Enrollment(Base):
    __tablename__ = 'enrollments'
    __table_args__ = (UniqueConstraint('user_id', 'course_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    role: Mapped[str] = mapped_column(String(20))


class Assignment(Base):
    __tablename__ = 'assignments'
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    title: Mapped[str] = mapped_column(String(200))
    description_md: Mapped[str] = mapped_column(Text)
    side_panel_md: Mapped[str] = mapped_column(Text)
    starter_code: Mapped[dict] = mapped_column(JSON)
    enabled_languages: Mapped[list] = mapped_column(JSON)
    intellisense_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    paste_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    checker_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    check_rules: Mapped[list] = mapped_column(JSON, default=list)
    show_results_to_student: Mapped[bool] = mapped_column(Boolean, default=False)
    diagnostics_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    lint_rules: Mapped[list] = mapped_column(JSON, default=list)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Draft(Base):
    __tablename__ = 'drafts'
    __table_args__ = (UniqueConstraint('assignment_id', 'student_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey('assignments.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    initial_code: Mapped[dict] = mapped_column(JSON)
    code: Mapped[dict] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    paste_blocked_count: Mapped[int] = mapped_column(Integer, default=0)
    blur_count: Mapped[int] = mapped_column(Integer, default=0)
    max_insert_chars: Mapped[int] = mapped_column(Integer, default=0)


class ReplayEvent(Base):
    __tablename__ = 'replay_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey('drafts.id'))
    t_ms: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSON)


class ReplayBatch(Base):
    __tablename__ = 'replay_batches'
    __table_args__ = (UniqueConstraint('draft_id', 'batch_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey('drafts.id'))
    batch_id: Mapped[str] = mapped_column(String(36))


class Submission(Base):
    __tablename__ = 'submissions'
    __table_args__ = (UniqueConstraint('assignment_id', 'student_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey('assignments.id'))
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    final_code: Mapped[dict] = mapped_column(JSON)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    locked: Mapped[bool] = mapped_column(Boolean, default=True)
    check_result: Mapped[list | None] = mapped_column(JSON, nullable=True)
    lint_report: Mapped[list | None] = mapped_column(JSON, nullable=True)
