from pydantic import BaseModel

class Category(BaseModel):
    CATEGORY_ID: int
    MAIN_CATEGORY: str
    SUB_CATEGORY: str
    DETAIL_CATEGORY: str

    class Config:
        from_attributes  = True
