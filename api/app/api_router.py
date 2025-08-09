from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import get_db

router = APIRouter(prefix="/api")

@router.post("/media/", response_model=schemas.Media)
def create_media(media: schemas.MediaCreate, db: Session = Depends(get_db)):
    user = crud.get_or_create_user(db, telegram_id=media.user_id, username=media.username)
    # Створюємо копію media з правильним user_id
    media_data = media.model_dump()
    media_data["user_id"] = user.id
    return crud.create_media(db=db, media=schemas.MediaCreate(**media_data))