from sqlalchemy.orm import Session
from . import models, schemas

def create_media(db: Session, media: schemas.MediaCreate):
    data = media.model_dump()
    data.pop("username", None)  # Видаляємо username, якщо є
    db_media = models.Media(**data)
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

from typing import Optional

def get_or_create_user(db: Session, telegram_id: int, username: Optional[str] = None):
    user = db.query(models.User).filter_by(telegram_id=telegram_id).first()
    if user is None:
        user = models.User(telegram_id=telegram_id, username=username or "")
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Оновлюємо username, якщо він змінився
        if username is not None and getattr(user, "username", None) != username:
            setattr(user, "username", username)
            db.commit()
    return user