from fastapi import APIRouter, HTTPException
from app.crud.insert import insert_record

router = APIRouter()

@router.get("/test-db")
async def test_db():
    try:
        insert_record(
            'users',
            id=1,
            name="John Doe")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
