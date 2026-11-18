from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Language = Literal['html', 'css', 'javascript']
HtmlTag = Literal['a', 'article', 'button', 'div', 'footer', 'form', 'h1', 'h2', 'h3', 'header', 'img', 'input', 'label', 'li', 'main', 'nav', 'ol', 'option', 'p', 'section', 'select', 'span', 'table', 'tbody', 'td', 'textarea', 'th', 'thead', 'tr', 'ul']


class CheckRule(BaseModel):
    id: UUID
    tag: HtmlTag
    attrs: dict[Literal['type', 'name', 'required', 'placeholder'], str] = Field(default_factory=dict, max_length=4)
    min_count: int = Field(default=1, ge=1, le=100)
    non_empty: bool = False
    inside: HtmlTag | None = None
    label_linked: bool = False

    @field_validator('attrs')
    @classmethod
    def validate_attributes(cls, attrs):
        if any(len(value) > 200 for value in attrs.values()):
            raise ValueError('Attribute value too long')
        if 'required' in attrs and attrs['required'] != '':
            raise ValueError('Required is a presence check')
        return attrs

    @model_validator(mode='after')
    def validate_label(self):
        if self.label_linked and self.tag != 'input':
            raise ValueError('Label association applies to inputs')
        return self


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
    checker_enabled: bool = False
    check_rules: list[CheckRule] = Field(default_factory=list, max_length=100)
    show_results_to_student: bool = False
    due_at: datetime | None = None

    @field_validator('check_rules')
    @classmethod
    def unique_rules(cls, rules):
        if rules is not None and len({rule.id for rule in rules}) != len(rules):
            raise ValueError('Rule IDs must be unique')
        return rules


class AssignmentOut(AssignmentInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    check_rules: list[CheckRule] | None = None


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
