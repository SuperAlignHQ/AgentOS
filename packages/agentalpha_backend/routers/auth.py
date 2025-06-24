from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List
from models.models import User
from database import get_session
from utils.auth_utils import verify_password,create_access_token,get_password_hash
from uuid import uuid4 
from pydantic import BaseModel

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str
    

@router.post("/register", response_model=User)
def register_user(user:RegisterRequest):
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.name == user.username)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        
        new_user = User(
            id=uuid4(),
            name=user.username,
            role=user.role,
            hashedPassword=get_password_hash(user.password),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
           
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

@router.post("/login")
def login_user(user1:LoginRequest):
    with get_session() as session:
        user = session.exec(select(User).where(User.name == user1.username)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")

        if not verify_password(user1.password, user.hashedPassword):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout_user():
    #Should implement in frontend part
    return {"message": "Successfully logged out"}










