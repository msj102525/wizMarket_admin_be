from pydantic import BaseModel


class Reference(BaseModel):
    reference_id: int
    reference_name: str
    reference_url: str

    class Config:
        from_attributes = True
