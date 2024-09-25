from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommonInformation(BaseModel):
    common_information_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    file_group_id: Optional[int] = None
    is_deleted: str = "N"
    etc: Optional[str] = None
    reg_id: Optional[int] = None
    reg_date: Optional[datetime] = None
    mod_id: Optional[int] = None
    mod_date: Optional[datetime] = None

    class Config:
        from_attributes = True
