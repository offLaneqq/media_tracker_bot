from typing import Optional
from pydantic import BaseModel

class MediaCreate(BaseModel):
    title: str
    title_en: str
    category: str
    status: str
    current_episode: int
    user_id: int
    username: str = ""

class Media(MediaCreate):
    id: int

    class Config:
        from_attributes = True

class MediaUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    current_episode: Optional[int] = None
    user_id: Optional[int] = None
    username: Optional[str] = None