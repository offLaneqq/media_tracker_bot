from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/media/")
def get_media(telegram_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if not user:
        return []
    return db.query(models.Media).filter(models.Media.user_id == user.id).all()

@router.patch("/media/{media_id}/", response_model=schemas.Media)
def update_media(media_id: int, media: schemas.MediaUpdate, db: Session = Depends(get_db)):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if not db_media:
        raise HTTPException(status_code=404, detail="Media not found")
    for field, value in media.model_dump(exclude_unset=True).items():
        setattr(db_media, field, value)
    db.commit()
    db.refresh(db_media)
    return db_media

@router.delete("/media/{media_id}/", status_code=204)
def delete_media(media_id: int, db: Session = Depends(get_db)):
    db_media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if not db_media:
        raise HTTPException(status_code=404, detail="Media not found")
    db.delete(db_media)
    db.commit()
    return