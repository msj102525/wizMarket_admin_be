from fastapi import APIRouter, HTTPException
from app.service.loc_info import *
from app.schemas.loc_info import *
from fastapi import Request


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


@router.post("/select_loc_info")
async def filter_data(filters: FilterRequest):
    # 입력된 값만 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)

    # 필터 데이터를 서비스 레이어로 전달
    result = await filter_location_info(filters_dict)

    return {"filtered_data": result}