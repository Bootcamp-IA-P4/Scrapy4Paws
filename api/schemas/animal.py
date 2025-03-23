from pydantic import BaseModel
from typing import Optional

class AnimalBase(BaseModel):
    name: str
    age: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    image: Optional[str] = None
    is_adopted: bool

class AnimalResponse(AnimalBase):
    id: int

    class Config:
        from_attributes = True