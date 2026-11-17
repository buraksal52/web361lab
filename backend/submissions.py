from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from drafts import student_assignment
from identity import current_user, require_enrollment
from models import Assignment, Draft, ReplayEvent, Submission, User
from schemas import CodeFiles

router = APIRouter()


def teacher_assignment(assignment_id: int, user: User, db: Session):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    require_enrollment(user, assignment.course_id, db, 'teacher')
    return assignment


@router.post('/assignments/{assignment_id}/submit')
def submit(assignment_id: int, code: CodeFiles, user: User = Depends(current_user), db: Session = Depends(get_db)):
    student_assignment(assignment_id, user, db)
    draft = db.scalar(select(Draft).where(Draft.assignment_id == assignment_id, Draft.student_id == user.id).with_for_update())
    if draft is None:
        raise HTTPException(404, 'Taslak bulunamadı.')
    submission = db.scalar(select(Submission).where(Submission.assignment_id == assignment_id, Submission.student_id == user.id))
    if submission and submission.locked:
        raise HTTPException(409, 'Ödev zaten teslim edildi.')
    if draft.code != code.model_dump():
        raise HTTPException(409, 'Son değişiklikler henüz kaydedilmedi.')
    now = datetime.now(timezone.utc)
    if submission is None:
        submission = Submission(assignment_id=assignment_id, student_id=user.id, final_code=draft.code, submitted_at=now, locked=True)
        db.add(submission)
    else:
        submission.final_code = draft.code
        submission.submitted_at = now
        submission.locked = True
    started = draft.started_at if draft.started_at.tzinfo else draft.started_at.replace(tzinfo=timezone.utc)
    elapsed = min(2147483647, max(0, int((now - started).total_seconds() * 1000)))
    db.add(ReplayEvent(draft_id=draft.id, t_ms=elapsed, kind='submit', payload={}))
    db.commit()
    return {'id': submission.id, 'locked': submission.locked, 'submitted_at': submission.submitted_at.isoformat()}


@router.get('/assignments/{assignment_id}/submissions')
def list_submissions(assignment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    teacher_assignment(assignment_id, user, db)
    rows = db.execute(select(Submission, User).join(User, User.id == Submission.student_id).where(Submission.assignment_id == assignment_id).order_by(User.name)).all()
    return [{'id': submission.id, 'student_id': student.id, 'student_name': student.name,
             'submitted_at': submission.submitted_at.isoformat(), 'locked': submission.locked} for submission, student in rows]


@router.get('/submissions/{submission_id}')
def get_submission(submission_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, 'Teslim bulunamadı.')
    assignment = db.get(Assignment, submission.assignment_id)
    enrollment = require_enrollment(user, assignment.course_id, db)
    if user.id != submission.student_id and enrollment.role != 'teacher':
        raise HTTPException(403, 'Bu işlem için yetkiniz yok.')
    student = db.get(User, submission.student_id)
    return {'id': submission.id, 'assignment_id': submission.assignment_id, 'student_id': submission.student_id,
            'student_name': student.name, 'final_code': submission.final_code,
            'submitted_at': submission.submitted_at.isoformat(), 'locked': submission.locked}


@router.post('/submissions/{submission_id}/unlock')
def unlock_submission(submission_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, 'Teslim bulunamadı.')
    teacher_assignment(submission.assignment_id, user, db)
    db.scalar(select(Draft).where(Draft.assignment_id == submission.assignment_id, Draft.student_id == submission.student_id).with_for_update())
    submission.locked = False
    db.commit()
    return {'locked': False}
