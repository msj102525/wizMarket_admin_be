from fastapi import APIRouter, HTTPException
from app.service.loc_info import get_location_data
from app.schemas.loc_info import LocationRequest

router = APIRouter()

@router.post('/get_loc_info')
async def get_loc_info(location: LocationRequest):
    try:
        loc_info = get_location_data(location.city_name, location.district_name, location.sub_district_name)
        return loc_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")