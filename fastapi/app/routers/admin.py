from fastapi import APIRouter

router = APIRouter(prefix="/admin")


@router.get("/login")
async def login():
    return {"message": "music"}


