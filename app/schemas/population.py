from pydantic import BaseModel

class Population(BaseModel):
    POP_ID: int
    ID: int
    GENDER: str
    OTO9: int
    TOTO19: int
    TOTO29: int
    TOTO39: int
    TOTO49: int
    TOTO59: int
    TOTO69: int
    TOTO79: int
    TOTO89: int
    TOTO99: int
    TOTO109: int
    TOTAL: int
    MALETOTAL: int
    FEMALETOTAL: int
    YEAR_MONTH: int

    class Config:
        from_attributes = True  # 기존 orm_mode = True 에서 변경
