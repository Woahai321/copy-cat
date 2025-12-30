from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import User

import os

# Security Configuration
# WARNING: In production, always set JWT_SECRET_KEY in your environment!
DEFAULT_SECRET = "CHANGE_THIS_TO_A_SECURE_RANDOM_STRING"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", DEFAULT_SECRET)

if SECRET_KEY == DEFAULT_SECRET:
    print("WARNING: Using default insecure SECRET_KEY. Please set JWT_SECRET_KEY in environment.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days expiration

security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    print(f"LOGIN ATTEMPT: username='{username}', password length={len(password)}")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Auth failed: User {username} not found")
        return False
    
    is_valid = verify_password(password, user.password_hash)
    if not is_valid:
        print(f"Auth failed: Invalid password for {username}")
        # DEBUG: Print hashes for debugging (REMOVE IN PRODUCTION)
        # print(f"  Input Hash: {get_password_hash(password)}")
        # print(f"  Stored Hash: {user.password_hash}")
        return False
    
    print(f"LOGIN SUCCESS: {username} authenticated")
    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

