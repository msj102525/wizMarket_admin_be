from pydantic import BaseModel
from typing import Optional

class City(BaseModel):
    city_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True
