from fastapi import APIRouter
import asyncio

router = APIRouter()

@router.get("/")
async def read_hello():
    await asyncio.sleep(3)
    return {"message": "hello"}
