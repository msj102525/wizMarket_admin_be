from fastapi import APIRouter, HTTPException
from app.service.crime import fetch_crime_data
from app.schemas.crime import CrimeRequest, Crime

router = APIRouter()

@router.post("/get_crime", response_model=list[Crime])
async def get_crime(crime_request: CrimeRequest):
    try:
        crime_data = fetch_crime_data(crime_request)
        if not crime_data:
            raise HTTPException(status_code=404, detail="City not found")
        return crime_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))