from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.service import movepop

router = APIRouter()

class Keyword(BaseModel):
    keyword: str

@router.post('/enter-keyword')
async def enter_keyword(data: Keyword):
    keyword = data.keyword

    try:
        result = movepop.crawl_keyword(keyword)
        return {"message": "Keyword entered successfully", "data": result}
    except Exception as e:
        print(f'Error: {e}')
        raise HTTPException(status_code=500, detail="Failed to enter keyword")
