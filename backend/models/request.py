from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
import re

class CreateStudentRequestBody(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if re.match(r'^[a-zA-Z.]+(\s[a-zA-Z.]+)*$', value):
            return value
        raise ValueError("Student name is invalid")