import csv
import io
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from identity import current_user, require_enrollment
from models import Assignment, CriterionResult, Evaluation, Submission, User
from schemas import EvaluationInput
from submissions import criteria_snapshot, teacher_assignment

router = APIRouter()


def same_instant(first: datetime, second: datetime):
    def utc(value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return utc(first) == utc(second)


def evaluation_is_current(evaluation: Evaluation, submission: Submission):
    return submission.locked and same_instant(evaluation.source_submitted_at, submission.submitted_at)


def get_submission_and_assignment(submission_id: int, db: Session):
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, 'Teslim bulunamadı.')
    return submission, db.get(Assignment, submission.assignment_id)


def rubric_for_submission(submission: Submission, assignment: Assignment):
    return submission.rubric_snapshot if submission.rubric_snapshot is not None else criteria_snapshot(assignment)


def rubric_fingerprint(snapshot, checker_enabled):
    encoded = json.dumps({'criteria': snapshot, 'checker_enabled': checker_enabled}, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def automatic_results(submission: Submission, assignment: Assignment):
    if not assignment.checker_enabled or submission.check_result is None:
        return {}
    return {str(item['rule']['id']): bool(item['used']) for item in submission.check_result}


def build_rows(submission: Submission, assignment: Assignment, evaluation: Evaluation | None):
    snapshot = rubric_for_submission(submission, assignment)
    recorded = {result.criterion_id: result for result in evaluation.results} if evaluation and evaluation_is_current(evaluation, submission) else {}
    auto = automatic_results(submission, assignment)
    rows = []
    for criterion in snapshot:
        saved = recorded.get(criterion['id'])
        auto_result = auto.get(criterion['check_rule_ref']) if criterion['kind'] == 'auto' else None
        override = saved.teacher_override if saved else None
        points = saved.points if saved and criterion['kind'] == 'manual' else None
        if criterion['kind'] == 'auto':
            effective = override if override is not None else auto_result
            points = Decimal(criterion['max_points']) if effective is True else Decimal('0') if effective is False else None
        rows.append({**criterion, 'auto_result': auto_result, 'teacher_override': override,
                     'points': str(points) if points is not None else None})
    return rows


def suggested_total(rows):
    if any(row['points'] is None for row in rows):
        return None
    return sum((Decimal(row['points']) for row in rows), Decimal('0.00'))


@router.get('/submissions/{submission_id}/evaluation')
def get_evaluation(submission_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    submission, assignment = get_submission_and_assignment(submission_id, db)
    require_enrollment(user, assignment.course_id, db, 'teacher')
    evaluation = db.scalar(select(Evaluation).where(Evaluation.submission_id == submission.id))
    current = evaluation is not None and evaluation_is_current(evaluation, submission)
    rows = build_rows(submission, assignment, evaluation)
    suggested = suggested_total(rows)
    previous = None
    if evaluation is not None and not current:
        previous = {'final_points': str(evaluation.final_points), 'feedback': evaluation.feedback,
                    'graded_at': evaluation.graded_at.isoformat()}
    return {'criteria': rows, 'suggested_points': str(suggested) if suggested is not None else None,
            'final_points': str(evaluation.final_points) if current else None,
            'feedback': evaluation.feedback if current else '', 'locked': submission.locked,
            'submitted_at': submission.submitted_at.isoformat(),
            'rubric_fingerprint': rubric_fingerprint(rubric_for_submission(submission, assignment), assignment.checker_enabled),
            'previous_evaluation': previous, 'uses_current_assignment_criteria': submission.rubric_snapshot is None}


@router.put('/submissions/{submission_id}/evaluation')
def save_evaluation(submission_id: int, data: EvaluationInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    submission = db.scalar(select(Submission).where(Submission.id == submission_id).with_for_update())
    if submission is None:
        raise HTTPException(404, 'Teslim bulunamadı.')
    assignment = db.get(Assignment, submission.assignment_id)
    require_enrollment(user, assignment.course_id, db, 'teacher')
    if not submission.locked:
        raise HTTPException(409, 'Değerlendirme için ödevin teslim edilmiş olması gerekiyor.')
    snapshot = rubric_for_submission(submission, assignment)
    if not same_instant(data.submitted_at, submission.submitted_at) or data.rubric_fingerprint != rubric_fingerprint(snapshot, assignment.checker_enabled):
        raise HTTPException(409, 'Teslim veya kriterler değişti; değerlendirmeyi yeniden açın.')
    inputs = {str(item.criterion_id): item for item in data.criteria}
    if len(inputs) != len(data.criteria) or set(inputs) != {item['id'] for item in snapshot}:
        raise HTTPException(422, 'Tüm kriterler bir kez değerlendirilmelidir.')
    auto = automatic_results(submission, assignment)
    calculated = []
    for criterion in snapshot:
        item = inputs[criterion['id']]
        maximum = Decimal(criterion['max_points'])
        auto_result = auto.get(criterion['check_rule_ref']) if criterion['kind'] == 'auto' else None
        if criterion['kind'] == 'auto':
            if item.manual_points is not None:
                raise HTTPException(422, 'Otomatik kriterlere kısmi puan verilemez.')
            effective = item.teacher_override if item.teacher_override is not None else auto_result
            if effective is None:
                raise HTTPException(422, 'Kontrol sonucu olmayan otomatik kriter için seçim yapın.')
            points = maximum if effective else Decimal('0.00')
        else:
            if item.teacher_override is not None or item.manual_points is None or item.manual_points > maximum:
                raise HTTPException(422, 'Manuel kriter puanı azami puanı aşmamalıdır.')
            points = item.manual_points
        calculated.append((criterion, item, auto_result, points))
    suggested = sum((row[3] for row in calculated), Decimal('0.00'))
    if submission.rubric_snapshot is None:
        submission.rubric_snapshot = snapshot
    evaluation = db.scalar(select(Evaluation).where(Evaluation.submission_id == submission.id))
    if evaluation is None:
        evaluation = Evaluation(submission_id=submission.id)
        db.add(evaluation)
    evaluation.suggested_points = suggested
    evaluation.final_points = data.final_points
    evaluation.feedback = data.feedback
    evaluation.graded_at = datetime.now(timezone.utc)
    evaluation.source_submitted_at = submission.submitted_at
    evaluation.criteria_snapshot = snapshot
    existing = {result.criterion_id: result for result in evaluation.results}
    results = []
    for position, (criterion, item, auto_result, points) in enumerate(calculated):
        result = existing.get(criterion['id']) or CriterionResult(criterion_id=criterion['id'])
        result.auto_result = auto_result
        result.teacher_override = item.teacher_override
        result.points = points
        result.position = position
        results.append(result)
    evaluation.results = results
    db.commit()
    return {'suggested_points': str(suggested), 'final_points': str(data.final_points), 'feedback': data.feedback}


@router.get('/submissions/{submission_id}/feedback')
def get_feedback(submission_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    submission, assignment = get_submission_and_assignment(submission_id, db)
    enrollment = require_enrollment(user, assignment.course_id, db)
    if user.id != submission.student_id and enrollment.role != 'teacher':
        raise HTTPException(403, 'Bu işlem için yetkiniz yok.')
    evaluation = db.scalar(select(Evaluation).where(Evaluation.submission_id == submission.id))
    if evaluation is None or not evaluation_is_current(evaluation, submission):
        return {'final_points': None, 'feedback': None}
    return {'final_points': str(evaluation.final_points), 'feedback': evaluation.feedback}


def csv_cell(value):
    text = str(value or '')
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r', '\n')) else text


@router.get('/assignments/{assignment_id}/grades.csv')
def export_grades(assignment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    teacher_assignment(assignment_id, user, db)
    rows = db.execute(select(Submission, User, Evaluation).join(User, User.id == Submission.student_id)
                      .join(Evaluation, Evaluation.submission_id == Submission.id)
                      .where(Submission.assignment_id == assignment_id).order_by(User.name)).all()
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['Öğrenci', 'E-posta', 'Son puan', 'Geri bildirim'])
    for submission, student, evaluation in rows:
        if evaluation_is_current(evaluation, submission):
            writer.writerow([csv_cell(student.name), csv_cell(student.email), str(evaluation.final_points), csv_cell(evaluation.feedback)])
    return Response(output.getvalue().encode('utf-8-sig'), media_type='text/csv',
                    headers={'Content-Disposition': f'attachment; filename="grades-{assignment_id}.csv"'})
