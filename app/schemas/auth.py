from pydantic import BaseModel, ConfigDict, Field, EmailStr
from models import RoleEnum


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    role: RoleEnum = RoleEnum.STUDENT


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    roll_no: str = Field(min_length=5, max_length=20)
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    semester: int = Field(gt=0, lt=10)

class StudentResponse(BaseModel):
    id: int
    roll_no: str
    name: str
    email: EmailStr
    semester: int

    model_config = ConfigDict(from_attributes=True)




class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

    