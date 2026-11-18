from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Language = Literal['html', 'css', 'javascript']
HtmlTag = Literal['a', 'article', 'button', 'div', 'footer', 'form', 'h1', 'h2', 'h3', 'header', 'img', 'input', 'label', 'li', 'main', 'nav', 'ol', 'option', 'p', 'section', 'select', 'span', 'table', 'tbody', 'td', 'textarea', 'th', 'thead', 'tr', 'ul']
LintRule = Literal['html_tag_pair', 'html_id_unique', 'html_alt', 'html_doctype', 'html_presentational', 'css_syntax', 'css_unknown_property', 'css_invalid_value', 'js_syntax', 'js_eqeqeq', 'js_unused', 'js_undef', 'indentation']


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


class CriterionInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: Literal['auto', 'manual']
    label: str = Field(min_length=1, max_length=200)
    max_points: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    check_rule_ref: UUID | None = None

    @model_validator(mode='after')
    def validate_rule_reference(self):
        if (self.kind == 'auto') != (self.check_rule_ref is not None):
            raise ValueError('Automatic criteria require a check rule; manual criteria cannot reference one')
        return self


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
    show_criteria_to_student: bool = False
    diagnostics_enabled: bool = False
    lint_rules: list[LintRule] = Field(default_factory=list, max_length=13)
    criteria: list[CriterionInput] = Field(default_factory=list, max_length=100)
    due_at: datetime | None = None

    @field_validator('check_rules')
    @classmethod
    def unique_rules(cls, rules):
        if rules is not None and len({rule.id for rule in rules}) != len(rules):
            raise ValueError('Rule IDs must be unique')
        return rules

    @model_validator(mode='after')
    def validate_criteria(self):
        if self.criteria is None:
            return self
        if len({criterion.id for criterion in self.criteria}) != len(self.criteria):
            raise ValueError('Criterion IDs must be unique')
        rule_ids = {rule.id for rule in self.check_rules or []}
        if self.check_rules is not None and any(criterion.check_rule_ref not in rule_ids for criterion in self.criteria if criterion.kind == 'auto'):
            raise ValueError('Automatic criteria must reference an existing check rule')
        return self


class AssignmentOut(AssignmentInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    check_rules: list[CheckRule] | None = None
    lint_rules: list[LintRule] | None = None
    criteria: list[CriterionInput] | None = None


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


class CriterionScoreInput(BaseModel):
    criterion_id: UUID
    manual_points: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    teacher_override: bool | None = None


class EvaluationInput(BaseModel):
    final_points: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    feedback: str = Field(default='', max_length=5000)
    submitted_at: datetime
    rubric_fingerprint: str = Field(min_length=64, max_length=64)
    criteria: list[CriterionScoreInput] = Field(max_length=100)
