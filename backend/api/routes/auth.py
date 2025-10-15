from fastapi import APIRouter,  HTTPException,  Depends
from backend.services.auth import login, register, get_all_users#, reset_all_passwords
from sqlmodel import Session, select
from backend.services.db import get_session
from backend.services.rate_limiter import rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(username: str, password: str, email: str,session: Session = Depends(get_session)):
    try:
        user = register(username, email, password, session=session)
        return {"message": "User registered successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/login")
async def login_user(username: str, password: str, session: Session = Depends(get_session)): 

    result = login(username, password, session=session)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result
@router.get("/users")
async def list_users(session: Session = Depends(get_session)):
    users = get_all_users(session=session)
    return {"users": users}

#@router.post("/reset_passwords")
#def reset_passwords():
#    reset_all_passwords()
