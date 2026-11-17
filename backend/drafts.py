from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from identity import current_user, require_enrollment
from models import Assignment, Draft, ReplayBatch, ReplayEvent, Submission, User
from schemas import DraftBatch

router = APIRouter()


@router.get('/me')
def me(user: User = Depends(current_user)):
    return {'id': user.id, 'name': user.name, 'role': user.role, 'recording_consent': user.recording_consent_at is not None}


@router.post('/me/recording-consent')
def recording_consent(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role != 'student':
        raise HTTPException(403, 'Bu işlem öğrenciler içindir.')
    if user.recording_consent_at is None:
        user.recording_consent_at = datetime.now(timezone.utc)
        db.commit()
    return {'recording_consent': True}


def student_assignment(assignment_id: int, user: User, db: Session):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    require_enrollment(user, assignment.course_id, db, 'student')
    if user.recording_consent_at is None:
        raise HTTPException(403, 'Kayıt bilgilendirmesini önce onaylamanız gerekiyor.')
    return assignment


def draft_response(draft: Draft):
    return {'id': draft.id, 'code': draft.code, 'initial_code': draft.initial_code,
            'started_at': draft.started_at.isoformat(), 'updated_at': draft.updated_at.isoformat(),
            'signals': {'paste_blocked_count': draft.paste_blocked_count, 'blur_count': draft.blur_count,
                        'max_insert_chars': draft.max_insert_chars}}


@router.post('/assignments/{assignment_id}/draft')
def open_draft(assignment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = student_assignment(assignment_id, user, db)
    draft = db.scalar(select(Draft).where(Draft.assignment_id == assignment_id, Draft.student_id == user.id))
    if draft is None:
        draft = Draft(assignment_id=assignment_id, student_id=user.id,
                      initial_code=assignment.starter_code, code=assignment.starter_code)
        db.add(draft)
        db.commit()
        db.refresh(draft)
    submission = db.scalar(select(Submission).where(Submission.assignment_id == assignment_id, Submission.student_id == user.id))
    return {**draft_response(draft), 'locked': bool(submission and submission.locked)}


def apply_changes(code: str, changes):
    data = code.encode('utf-16-le', 'surrogatepass')
    for change in changes:
        start = change.rangeOffset * 2
        end = start + change.rangeLength * 2
        if start > len(data) or end > len(data):
            raise HTTPException(400, 'Düzenleme aralığı geçersiz.')
        data = data[:start] + change.text.encode('utf-16-le', 'surrogatepass') + data[end:]
    return data.decode('utf-16-le', 'surrogatepass')


@router.post('/assignments/{assignment_id}/draft/batches')
def save_batch(assignment_id: int, batch: DraftBatch, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = student_assignment(assignment_id, user, db)
    draft = db.scalar(select(Draft).where(Draft.assignment_id == assignment_id, Draft.student_id == user.id).with_for_update())
    if draft is None:
        raise HTTPException(404, 'Taslak bulunamadı.')
    batch_id = str(batch.batch_id)
    if db.scalar(select(ReplayBatch.id).where(ReplayBatch.draft_id == draft.id, ReplayBatch.batch_id == batch_id)) is not None:
        return draft_response(draft)
    submission = db.scalar(select(Submission).where(Submission.assignment_id == assignment_id, Submission.student_id == user.id))
    if submission and submission.locked:
        raise HTTPException(409, 'Teslim edilen ödev düzenlenemez.')
    code = dict(draft.code)
    for event in batch.events:
        if event.kind == 'edit':
            language = event.payload.language
            changes = event.payload.changes
            if language not in assignment.enabled_languages or not changes:
                raise HTTPException(400, 'Düzenleme verisi geçersiz.')
            code[language] = apply_changes(code[language], changes)
            draft.max_insert_chars = max(draft.max_insert_chars, *(len(change.text) for change in changes))
        elif event.kind == 'paste_blocked':
            draft.paste_blocked_count += 1
        elif event.kind == 'blur':
            draft.blur_count += 1
        db.add(ReplayEvent(draft_id=draft.id, t_ms=event.t_ms, kind=event.kind,
                           payload=event.payload.model_dump(exclude_none=True)))
    if code != batch.code.model_dump():
        raise HTTPException(400, 'Taslak ve düzenleme olayları eşleşmiyor.')
    draft.code = code
    draft.updated_at = datetime.now(timezone.utc)
    db.add(ReplayBatch(draft_id=draft.id, batch_id=batch_id))
    db.commit()
    db.refresh(draft)
    return draft_response(draft)


@router.get('/assignments/{assignment_id}/students/{student_id}/replay')
def get_replay(assignment_id: int, student_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    enrollment = require_enrollment(user, assignment.course_id, db)
    if user.id != student_id and enrollment.role != 'teacher':
        raise HTTPException(403, 'Bu işlem için yetkiniz yok.')
    draft = db.scalar(select(Draft).where(Draft.assignment_id == assignment_id, Draft.student_id == student_id))
    if draft is None:
        raise HTTPException(404, 'Taslak bulunamadı.')
    events = db.scalars(select(ReplayEvent).where(ReplayEvent.draft_id == draft.id).order_by(ReplayEvent.id)).all()
    return {**draft_response(draft), 'events': [{'t_ms': e.t_ms, 'kind': e.kind, 'payload': e.payload} for e in events]}
