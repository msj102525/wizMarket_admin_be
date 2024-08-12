from fastapi import APIRouter, Request
from app.crud.population_data import insert_record
router = APIRouter()


@router.post("/receive-items")
async def receive_items(request: Request):
    try:
        data = await request.json()
        items = data['items']

        for item in items:
            insert_record("population_data", **item)

        return {"status": "success", "received_items": len(items)}
    except Exception as e:
        print('Error processing request:', e)
        return {"status": "error", "message": str(e)}
