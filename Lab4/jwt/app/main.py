from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, LoginHistory
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from pydantic import BaseModel
from datetime import datetime, timedelta
import redis
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для проверки JWT-токена
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

# Модели запросов
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UpdateUserRequest(BaseModel):
    email: str = None
    password: str = None

# Регистрация пользователя
@app.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# Аутентификация пользователя
@app.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})
    
    redis_client.setex(db_user.email, timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))), refresh_token)
    
    login_history = LoginHistory(user_id=db_user.id, user_agent="user_agent_placeholder", login_time=datetime.utcnow())
    db.add(login_history)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token}

# Обновление токена
@app.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    payload = decode_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    email = payload.get("sub")
    stored_refresh_token = redis_client.get(email)
    if not stored_refresh_token or stored_refresh_token.decode() != request.refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access_token = create_access_token({"sub": email})
    return {"access_token": new_access_token}

# Изменение данных пользователя
@app.put("/user/update")
def update_user(
    user_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_data.email:
        current_user.email = user_data.email
    if user_data.password:
        current_user.hashed_password = get_password_hash(user_data.password)
    
    db.commit()
    return {"message": "User updated successfully"}

# Просмотр истории входов
@app.get("/user/history")
def get_login_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history = db.query(LoginHistory).filter(LoginHistory.user_id == current_user.id).all()
    return [{"user_agent": entry.user_agent, "login_time": entry.login_time} for entry in history]

# Выход из системы
@app.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    redis_client.delete(current_user.email)
    return {"message": "Logged out successfully"}