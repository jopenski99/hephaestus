from fastapi import APIRouter, Depends, HTTPException
from backend.services.auth import login, register, get_all_users
from backend.services.rate_limiter import rate_limit

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(username: str, password: str):
    try:
        user = register(username, password)
        return {"message": "User registered successfully", "user": user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.post("/login")
async def login_user(username: str, password: str):
    result = login(username, password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    return result
@router.get("/users")
async def list_users():
    users = get_all_users()
    return {"users": users}
