import csv
import io
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from identity import current_user, provider, require_enrollment
from models import User

router = APIRouter()


class RosterInput(BaseModel):
    csv_text: str = Field(max_length=262144)


@router.post('/courses/{course_id}/students/import')
def import_roster(course_id: int, data: RosterInput, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_enrollment(user, course_id, db, 'teacher')
    try:
        reader = csv.DictReader(io.StringIO(data.csv_text.lstrip('\ufeff')), strict=True)
        if reader.fieldnames != ['student_number', 'name', 'email']:
            raise ValueError('Invalid columns')
        students = []
        numbers, emails = set(), set()
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Invalid row')
            number, name, email = (row[key].strip() for key in reader.fieldnames)
            if not re.fullmatch(r'[0-9]{9}', number) or not name or len(name) > 200 or len(email) > 320 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                raise ValueError('Invalid student')
            if number in numbers or email.lower() in emails or len(students) >= 1000:
                raise ValueError('Duplicate or too many students')
            numbers.add(number)
            emails.add(email.lower())
            students.append({'student_number': number, 'name': name, 'email': email.lower()})
        if not students:
            raise ValueError('Empty roster')
    except (csv.Error, ValueError):
        raise HTTPException(422, 'CSV geçersiz. student_number,name,email sütunları ve benzersiz 9 haneli numaralar kullanın.')
    return provider.import_students(students, course_id, db)
