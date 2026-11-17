from datetime import datetime
from typing import Literal

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
