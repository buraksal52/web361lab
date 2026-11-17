from sqlalchemy import select

from database import SessionLocal
from models import Course, Enrollment, User


def seed():
    with SessionLocal() as db:
        if db.scalar(select(Course.id).limit(1)) is not None:
            return
        teacher = User(name='Örnek Öğretim Elemanı', email='teacher@example.invalid', role='teacher')
        student = User(name='Örnek Öğrenci', email='student@example.invalid', role='student')
        outsider = User(name='Kayıtsız Öğrenci', email='outside@example.invalid', role='student')
        course = Course(name='Web Programlama')
        db.add_all([teacher, student, outsider, course])
        db.flush()
        db.add_all([Enrollment(user_id=teacher.id, course_id=course.id, role='teacher'), Enrollment(user_id=student.id, course_id=course.id, role='student')])
        db.commit()


if __name__ == '__main__':
    seed()
