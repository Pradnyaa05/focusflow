from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base
from sqlalchemy import Boolean

# USER TABLE
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))


# NOTES TABLE
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(String(255))

    user_id = Column(Integer, ForeignKey("users.id"))


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    is_completed = Column(Boolean, default=False)
    date = Column(String(50))

    user_id = Column(Integer, ForeignKey("users.id"))