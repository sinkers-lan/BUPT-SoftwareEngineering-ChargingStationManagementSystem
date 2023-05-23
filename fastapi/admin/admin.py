from fastapi import APIRouter

# 前缀不能以 / 作为结尾
router = APIRouter()


@router.get("/login")
async def login():
    return {"message": "music"}


