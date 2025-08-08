from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/media")
async def list_media():
    return []