from pydantic import BaseModel
from typing import Optional

class MediaCreate(BaseModel):
    title: str
    category: str
    status: str
    current_episode: int
    user_id: int
    username: str = ""

class Media(MediaCreate):
    id: int

    class Config:
        from_attributes = True