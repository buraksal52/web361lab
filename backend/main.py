from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from identity import bearer, current_user, provider, require_enrollment
from fastapi.security import HTTPAuthorizationCredentials
from models import Assignment, Course, Enrollment, User
from schemas import AssignmentInput, AssignmentOut
from drafts import router as drafts_router
from submissions import router as submissions_router

app = FastAPI()
app.include_router(drafts_router)
app.include_router(submissions_router)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['GET', 'POST', 'PUT'], allow_headers=['Authorization', 'Content-Type'])


@app.get('/hello')
def hello():
    return {'message': 'Merhaba'}


@app.get('/demo/users')
def demo_users(db: Session = Depends(get_db)):
    return [{'id': user.id, 'name': user.name, 'role': user.role} for user in db.scalars(select(User)).all()]


@app.post('/demo/login/{user_id}')
def demo_login(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(404, 'Kullanıcı bulunamadı.')
    return {'token': provider.login(user), 'name': user.name, 'role': user.role}


@app.post('/demo/logout')
def demo_logout(credentials: HTTPAuthorizationCredentials = Depends(bearer), user: User = Depends(current_user)):
    provider.logout(credentials.credentials)
    return {'ok': True}


@app.get('/courses')
def courses(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(Course, Enrollment.role).join(Enrollment, Enrollment.course_id == Course.id).where(Enrollment.user_id == user.id)).all()
    return [{'id': course.id, 'name': course.name, 'role': role} for course, role in rows]


def assignment_response(assignment: Assignment, role: str):
    result = AssignmentOut.model_validate(assignment).model_dump()
    if role != 'teacher' and not assignment.show_results_to_student:
        result['check_rules'] = None
    return result


def assignment_values(data: AssignmentInput):
    result = data.model_dump()
    result['check_rules'] = [rule.model_dump(mode='json') for rule in data.check_rules]
    return result


@app.get('/courses/{course_id}/assignments', response_model=list[AssignmentOut], response_model_exclude_none=True)
def list_assignments(course_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    enrollment = require_enrollment(user, course_id, db)
    return [assignment_response(assignment, enrollment.role) for assignment in db.scalars(select(Assignment).where(Assignment.course_id == course_id)).all()]


@app.get('/assignments/{assignment_id}', response_model=AssignmentOut, response_model_exclude_none=True)
def get_assignment(assignment_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    enrollment = require_enrollment(user, assignment.course_id, db)
    return assignment_response(assignment, enrollment.role)


@app.post('/assignments', response_model=AssignmentOut, status_code=201)
def create_assignment(data: AssignmentInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_enrollment(user, data.course_id, db, 'teacher')
    assignment = Assignment(**assignment_values(data))
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@app.put('/assignments/{assignment_id}', response_model=AssignmentOut)
def update_assignment(assignment_id: int, data: AssignmentInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(404, 'Ödev bulunamadı.')
    require_enrollment(user, assignment.course_id, db, 'teacher')
    if data.course_id != assignment.course_id:
        raise HTTPException(400, 'Ödevin dersi değiştirilemez.')
    for key, value in assignment_values(data).items():
        setattr(assignment, key, value)
    db.commit()
    db.refresh(assignment)
    return assignment
