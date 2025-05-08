from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, ForwardRef
from datetime import datetime

GroupRef = ForwardRef("Group")

class StudentBase(SQLModel):
    name: str
    age: int

class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: Optional[int] = Field(default=None, foreign_key="group.id")
    group: Optional[GroupRef] = Relationship(back_populates="students")


class GroupBase(SQLModel):
    name: str

class Group(GroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    students: List["Student"] = Relationship(back_populates="group")


Student.update_forward_refs()
Group.update_forward_refs()
