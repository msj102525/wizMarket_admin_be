from pydantic import BaseModel
from typing import Optional

class District(BaseModel):
    district_id: Optional[int]= None
    city_id: int
    name: str

    class Config:
        from_attributes = True
