from pydantic import BaseModel


class BizMainCategory(BaseModel):
    biz_main_category_id: int
    biz_main_category_name: str

    class Config:
        from_attributes = True
