from pydantic import BaseModel, EmailStr, Field

class StudentCreate(BaseModel):
    roll_no: str
    name: str
    email: EmailStr
    semester: int = Field(gt=0, lt=10)

class StudentResponse(BaseModel):
    id: int
    roll_no: str
    name: str
    email: EmailStr
    semester: int

    model_config = {
        "from_attributes": True
    }


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    semester: int | None = None