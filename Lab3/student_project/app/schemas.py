from pydantic import BaseModel
from typing import List, Optional

class StudentCreate(BaseModel):
    name: str
    age: int

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    group_id: Optional[int]

class GroupCreate(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: int
    name: str
    students: Optional[List[StudentResponse]] = []
    
   



