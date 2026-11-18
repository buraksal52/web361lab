from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from drafts import student_assignment
from identity import current_user, require_enrollment
from models import Assignment, Draft, ReplayEvent, Submission, User
from schemas import CodeFiles, CriterionInput
from checker import run_checker
from writing_checks import run_writing_checks

router = APIRouter()


def criteria_snapshot(assignment: Assignment):
    return [CriterionInput.model_validate(criterion).model_dump(mode='json') for criterion in assignment.criteria]


def teacher_assignment(assignment_id: int, user: User, db: Session):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    require_enrollment(user, assignment.course_id, db, 'teacher')
    return assignment


@router.post('/assignments/{assignment_id}/submit')
def submit(assignment_id: int, code: CodeFiles, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = student_assignment(assignment_id, user, db)
    draft = db.scalar(select(Draft).where(Draft.assignment_id == assignment_id, Draft.student_id == user.id).with_for_update())
    if draft is None:
        raise HTTPException(404, 'Taslak bulunamadı.')
    submission = db.scalar(select(Submission).where(Submission.assignment_id == assignment_id, Submission.student_id == user.id))
    if submission and submission.locked:
        raise HTTPException(409, 'Ödev zaten teslim edildi.')
    if draft.code != code.model_dump():
        raise HTTPException(409, 'Son değişiklikler henüz kaydedilmedi.')
    check_result = None
    if assignment.checker_enabled:
        try:
            check_result = run_checker(draft.code['html'], assignment.check_rules)
        except ValueError as error:
            raise HTTPException(413, str(error)) from error
        except (TimeoutError, RuntimeError, EOFError) as error:
            raise HTTPException(503, 'HTML kontrolü tamamlanamadı. Lütfen tekrar deneyin.') from error
    lint_report = None
    if assignment.lint_rules:
        try:
            lint_report = run_writing_checks(draft.code, assignment.lint_rules)
        except ValueError as error:
            raise HTTPException(413, str(error)) from error
        except RuntimeError as error:
            raise HTTPException(503, 'Yazım kontrolü tamamlanamadı. Lütfen tekrar deneyin.') from error
    now = datetime.now(timezone.utc)
    if submission is None:
        submission = Submission(assignment_id=assignment_id, student_id=user.id, final_code=draft.code, submitted_at=now, locked=True, check_result=check_result, lint_report=lint_report, rubric_snapshot=criteria_snapshot(assignment))
        db.add(submission)
    else:
        submission.final_code = draft.code
        submission.submitted_at = now
        submission.locked = True
        submission.check_result = check_result
        submission.lint_report = lint_report
        submission.rubric_snapshot = criteria_snapshot(assignment)
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
    result = {'id': submission.id, 'assignment_id': submission.assignment_id, 'student_id': submission.student_id,
            'student_name': student.name, 'final_code': submission.final_code,
            'submitted_at': submission.submitted_at.isoformat(), 'locked': submission.locked}
    if assignment.checker_enabled and (enrollment.role == 'teacher' or assignment.show_results_to_student):
        if submission.check_result is not None:
            result['check_result'] = submission.check_result
    if enrollment.role == 'teacher' and submission.lint_report is not None:
        result['lint_report'] = submission.lint_report
    return result


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
