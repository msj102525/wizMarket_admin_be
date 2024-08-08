from fastapi import APIRouter, HTTPException
from app.crud.select import select_wiz

router = APIRouter()

@router.get("/test-db")
async def test_db():
    try:
        result = select_wiz()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
