from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Language = Literal['html', 'css', 'javascript']


class CodeFiles(BaseModel):
    html: str = ''
    css: str = ''
    javascript: str = ''


class AssignmentInput(BaseModel):
    course_id: int
    title: str = Field(min_length=1, max_length=200)
    description_md: str = ''
    side_panel_md: str = ''
    starter_code: CodeFiles = CodeFiles()
    enabled_languages: list[Language] = Field(min_length=1, max_length=3)
    intellisense_enabled: bool = True
    paste_enabled: bool = True
    due_at: datetime | None = None


class AssignmentOut(AssignmentInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EditChange(BaseModel):
    rangeOffset: int = Field(ge=0)
    rangeLength: int = Field(ge=0)
    text: str


class ReplayPayload(BaseModel):
    language: Language | None = None
    changes: list[EditChange] | None = None


class ReplayEventInput(BaseModel):
    t_ms: int = Field(ge=0, le=2147483647)
    kind: Literal['edit', 'paste_blocked', 'blur', 'focus']
    payload: ReplayPayload = ReplayPayload()


class DraftBatch(BaseModel):
    batch_id: UUID
    code: CodeFiles
    events: list[ReplayEventInput] = Field(max_length=1000)
