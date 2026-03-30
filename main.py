from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from passlib.context import CryptContext
from auth import create_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware


from fastapi.staticfiles import StaticFiles

from database import engine
import models

models.Base.metadata.create_all(bind=engine)

# # CREATE TABLES
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
security = HTTPBearer()

# DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= AUTH =================

# @app.post("/register")
# def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     existing_user = db.query(models.User).filter(models.User.username == user.username).first()

#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username already exists")

#     hashed_password = pwd_context.hash(user.password)

#     new_user = models.User(username=user.username, password=hashed_password)

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {"message": "User created successfully"}

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 🔥 ADD THIS CHECK
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Password too long")

    # 🔥 FIXED HASHING
    hashed_password = pwd_context.hash(user.password[:72])

    new_user = models.User(
        username=user.username,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    if not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # 🔥 STORE USER ID
    # token = create_token({"sub": str(db_user.id)})
    token = create_token({
    "sub": str(db_user.id),
    "username": db_user.username
})

    return {"access_token": token, "token_type": "bearer"}


# ================= TOKEN =================

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "secret123", algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


# ================= PROFILE =================

@app.get("/profile")
def profile(user=Depends(verify_token)):
    return {"message": "Welcome!", "user": user}


# ================= NOTES CRUD =================

# CREATE
@app.post("/notes", response_model=schemas.NoteOut)
def create_note(note: schemas.NoteCreate,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    new_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=int(user["sub"])
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


# READ
@app.get("/notes", response_model=list[schemas.NoteOut])
def get_notes(db: Session = Depends(get_db),
              user=Depends(verify_token)):

    return db.query(models.Note).filter(
        models.Note.user_id == int(user["sub"])
    ).all()


# UPDATE
@app.put("/notes/{note_id}", response_model=schemas.NoteOut)
def update_note(note_id: int,
                updated_note: schemas.NoteUpdate,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == int(user["sub"])
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = updated_note.title
    note.content = updated_note.content

    db.commit()
    db.refresh(note)

    return note


# DELETE
@app.delete("/notes/{note_id}")
def delete_note(note_id: int,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == int(user["sub"])
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Deleted successfully"}


# ================= TODOS =================

@app.post("/todos", response_model=schemas.TodoOut)
def create_todo(todo: schemas.TodoCreate,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    new_todo = models.Todo(
        title=todo.title,
        date=todo.date,
        is_completed=False,
        user_id=int(user["sub"])
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo


@app.get("/todos", response_model=list[schemas.TodoOut])
def get_todos(db: Session = Depends(get_db),
              user=Depends(verify_token)):

    return db.query(models.Todo).filter(
        models.Todo.user_id == int(user["sub"])
    ).all()


@app.put("/todos/{todo_id}")
def toggle_todo(todo_id: int,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == int(user["sub"])
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.is_completed = not todo.is_completed

    db.commit()

    return {"message": "Todo updated"}


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int,
                db: Session = Depends(get_db),
                user=Depends(verify_token)):

    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.user_id == int(user["sub"])
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted"}


# ================= STATS =================

@app.get("/stats")
def get_stats(db: Session = Depends(get_db), user=Depends(verify_token)):
    user_id = int(user["sub"])

    # total notes
    total_notes = db.query(models.Note).filter(
        models.Note.user_id == user_id
    ).count()

    # total todos
    total_todos = db.query(models.Todo).filter(
        models.Todo.user_id == user_id
    ).count()

    # completed todos
    completed_todos = db.query(models.Todo).filter(
        models.Todo.user_id == user_id,
        models.Todo.is_completed == True
    ).count()

    return {
        "notes": total_notes,
        "todos": total_todos,
        "completed": completed_todos
    }

# ROOT
# @app.get("/")
# def home():
#     return {"message": "API is running 🚀"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")