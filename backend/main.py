# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from jose import JWTError, jwt

from . import models, schemas, auth
from .database import engine, get_db

# Automatically generate our local SQLite database tables on server start
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# Setup dependency injection for extracting secure OAuth2 tokens from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to fetch the current authenticated user making an API request
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


# --- 🔐 USER AUTHENTICATION ENDPOINTS ---

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username is already taken
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password and store user details securely
    hashed_pwd = auth.get_password_hash(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate the user details
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Issue a secure JWT access token
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# --- 📋 TASK CRUD MANAGEMENT ENDPOINTS ---

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create a new task tied specifically to the logged-in user
    new_task = models.Task(**task.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=List[schemas.TaskResponse])
def read_tasks(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Return only the tasks owned by the authenticated user
    return db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()


@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, updated_task: schemas.TaskCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Locate task ensuring it belongs strictly to the user
    task_query = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id)
    task = task_query.first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
        
    task_query.update(updated_task.model_dump(), synchronize_session=False)
    db.commit()
    return task_query.first()


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Locate task ensuring it belongs strictly to the user
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or unauthorized")
        
    db.delete(task)
    db.commit()
    return None