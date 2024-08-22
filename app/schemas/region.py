from pydantic import BaseModel

class Region(BaseModel):
    REGION_ID: int
    CITY: str
    DISTRICT: str
    SUB_DISTRICT: str

    class Config:
        orm_mode = True
