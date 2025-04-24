from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession 
from app.models import Student, Group
from app.schemas import StudentCreate, StudentResponse, GroupCreate, GroupResponse
from app.database import get_session, init_db
from typing import List

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.post("/students/", response_model=StudentResponse)
async def create_student(student: StudentCreate, session: Session = Depends(get_session)):
    db_student = Student(**student.dict())
    session.add(db_student)
    await session.commit()
    await session.refresh(db_student)
    return db_student
    
@app.get("/students/", response_model=List[StudentResponse])
async def get_students(session: Session = Depends(get_session)):
    result = await session.execute(select(Student))
    students = result.scalars().all()
    return students

@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, session: Session = Depends(get_session)):
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await session.delete(student)
    await session.commit()
    return {"message": "Student deleted"}

@app.post("/groups/", response_model=GroupResponse)
async def create_group(group: GroupCreate, session: Session = Depends(get_session)):
    try:
        db_group = Group(**group.dict())  
        session.add(db_group)            
        await session.commit()            
        await session.refresh(db_group)   
        return db_group                  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  

@app.get("/groups/", response_model=List[GroupResponse])
async def get_groups(session: Session = Depends(get_session)):
    result = await session.execute(select(Group))
    groups = result.scalars().all()
    return groups

@app.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, session: Session = Depends(get_session)):
    group = await session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@app.delete("/groups/{group_id}")
async def delete_group(group_id: int, session: Session = Depends(get_session)):
    group = await session.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    await session.delete(group)
    await session.commit()
    return {"message": "Group deleted"}

@app.post("/groups/{group_id}/add_student/{student_id}")
async def add_student_to_group(group_id: int, student_id: int, session: Session = Depends(get_session)):
    group = await session.get(Group, group_id)
    student = await session.get(Student, student_id)
    if not group or not student:
        raise HTTPException(status_code=404, detail="Group or Student not found")
    student.group_id = group_id
    await session.commit()
    return {"message": "Student added to group"}

@app.delete("/groups/{group_id}/remove_student/{student_id}")
async def remove_student_from_group(group_id: int, student_id: int, session: Session = Depends(get_session)):
    group = await session.get(Group, group_id)
    student = await session.get(Student, student_id)
    if not group or not student:
        raise HTTPException(status_code=404, detail="Group or Student not found")
    student.group_id = None
    await session.commit()
    return {"message": "Student removed from group"}

@app.get("/groups/{group_id}/students", response_model=List[StudentResponse])
async def get_students_in_group(group_id: int, session: AsyncSession = Depends(get_session)):
    try:
        group = await session.get(Group, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        
        result = await session.execute(
            select(Student).where(Student.group_id == group_id)
        )
        students = result.scalars().all()
        
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfer_student/{student_id}/from/{group_a_id}/to/{group_b_id}")
async def transfer_student(student_id: int, group_a_id: int, group_b_id: int, session: Session = Depends(get_session)):
    student = await session.get(Student, student_id)
    group_a = await session.get(Group, group_a_id)
    group_b = await session.get(Group, group_b_id)
    if not student or not group_a or not group_b:
        raise HTTPException(status_code=404, detail="Student or Group not found")
    if student.group_id != group_a_id:
        raise HTTPException(status_code=400, detail="Student is not in Group A")
    student.group_id = group_b_id
    await session.commit()
    return {"message": "Student transferred"}