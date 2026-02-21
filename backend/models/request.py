from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
import re

class CreateStudentRequestBody(BaseModel):
    student_number: str
    name: str
    email: EmailStr

    @field_validator("student_number")
    @classmethod
    def validate_student_number(cls, value):
        if re.match(r'^\d{4}-\d{3}-\d{3}$', value):
            return value
        raise ValueError("Student number is invalid")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if re.match(r'^[a-zA-Z]+(\s[a-zA-Z]+)*$', value):
            return value
        raise ValueError("Student name is invalid")