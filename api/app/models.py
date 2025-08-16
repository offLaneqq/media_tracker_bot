from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .database import Base

class MediaCategory(str, enum.Enum):
    anime = "anime"
    film = "film"
    book = "book"

class MediaStatus(str, enum.Enum):
    planned = "Заплановано"
    watching = "Дивлюсь"
    completed = "Переглянуто"

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    title_en = Column(String, index=True, nullable=True)
    category = Column(Enum(MediaCategory), index=True, nullable=False, default=MediaCategory.anime)
    status = Column(Enum(MediaStatus), index=True, nullable=False, default=MediaStatus.planned)
    current_episode = Column(Integer, index=True, nullable=False, default=1)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User", back_populates="media")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    
    media = relationship("Media", back_populates="user")