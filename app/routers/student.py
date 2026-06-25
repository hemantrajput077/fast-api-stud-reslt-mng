# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.dependencies import get_current_user
from app.logger import logger

router = APIRouter(tags=["Student"])

@router.post("/register")
def create_student(
    student : StudentCreate,
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user)
):
    logger.info(f"User '{current_user.username}' is attempting to register student with roll_no='{student.roll_no}'")
    existing = (
        db.query(Student)
        .filter(Student.roll_no == student.roll_no)
        .first()
    )
    if existing :
        logger.warning(f"Student registration failed: Roll number '{student.roll_no}' already exists")
        raise HTTPException(
            status_code=400,
            detail="Student already exists"
        )
    new_student = Student(
        roll_no=student.roll_no,
        name=student.name,
        email=student.email,
        semester=student.semester
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    logger.info(f"Student registered successfully: roll_no='{new_student.roll_no}', id={new_student.id}")
    return new_student


@router.get("/all-students", response_model=List[StudentResponse])
def get_all_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User '{current_user.username}' requested all students list")
    students = db.query(Student).all()
    logger.info(f"Retrieved {len(students)} students")
    return students

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User '{current_user.username}' requested details for student_id={student_id}")
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        logger.warning(f"Student fetch failed: student_id={student_id} not found")
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    return student

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User '{current_user.username}' is updating student_id={student_id}")
    existing = db.query(Student).filter(Student.id == student_id).first()
    if not existing:
        logger.warning(f"Student update failed: student_id={student_id} not found")
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student.name is not None:
        existing.name = student.name

    if student.email is not None:
        existing.email = student.email

    if student.semester is not None:
        existing.semester = student.semester

    db.commit()
    db.refresh(existing)
    logger.info(f"Student updated successfully: student_id={student_id}")
    return existing

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"User '{current_user.username}' is deleting student_id={student_id}")
    existing = db.query(Student).filter(Student.id == student_id).first()
    if not existing:
        logger.warning(f"Student deletion failed: student_id={student_id} not found")
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    db.delete(existing)
    db.commit()
    logger.info(f"Student deleted successfully: student_id={student_id}")
    return {"message": "Student deleted successfully"}
