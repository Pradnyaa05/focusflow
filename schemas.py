# from pydantic import BaseModel

# class UserCreate(BaseModel):
#     username: str
#     password: str

# class UserLogin(BaseModel):
#     username: str
#     password: str

from pydantic import BaseModel

# AUTH
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


# NOTES
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    title: str
    date: str

class TodoOut(BaseModel):
    id: int
    title: str
    is_completed: bool
    date: str

    class Config:
        from_attributes = True