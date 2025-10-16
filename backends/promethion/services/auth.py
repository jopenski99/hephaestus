from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException,  Depends, Header
from sqlmodel import Session, select

from promethion.models.user import User
from promethion.api.core.config import settings
from promethion.services.db import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET = settings.JWT_SECRET
ALGO = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str) -> str:
    password_lmtd = password[:72]  # bcrypt limit
    return pwd_context.hash(password_lmtd)
    

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def login(username: str, password: str,session: Session, expires_delta: timedelta | None = None, ):
    
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        return {"message": "Invalid credentials", "success": False}
    expires = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token = jwt.encode({"sub": user.username,"exp": expires}, SECRET, algorithm=ALGO)
    user_detail = { "username": user.username, "email": user.email}
    return { "data" : {"access_token": token, "token_type": "bearer", "user": user_detail }, "success": True }

def get_all_users(session: Session):
    users = session.exec(select(User)).all()
    return users

def register(username: str, email: str,  password: str, session: Session, is_superuser: bool = False):
    try:
        user = session.exec(select(User).where(User.username == username)).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already taken")
        user = User(username=username, email=email, password_hash=hash_password(password), is_superuser=is_superuser)
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

    return {"message": "✅ User registered", "user_id": user}

async def verify_token(authorization: str = Header(None), session: Session = Depends(get_session)):
   
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.split(" ")[1]
    username = verify_jwt(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        return None
    print(user.username, user.is_superuser) 
    return {
        "username": user.username,
        "su": user.is_superuser
    }
    # You can return username or a full user object if needed
    return username
def verify_jwt(token: str = None):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        username = payload.get("sub")

        if username is None:
            return None
        return username
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None