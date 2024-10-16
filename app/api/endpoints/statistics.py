from fastapi import APIRouter, HTTPException
from app.service.statistics import *
from app.schemas.loc_info import *
from fastapi import Request


router = APIRouter()



@router.post("/select_statistics")
async def filter_data(filters: FilterRequest):
    # 입력된 값만 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)

    city = filters_dict.get('city')
    district = filters_dict.get('district')
    sub_district = filters_dict.get('subDistrict')

    if city is None:
        result = select_stat_data(filters_dict)
    elif district is None:
        result = select_stat_data_by_city(filters_dict)
    elif sub_district is None:
        result = select_stat_data_by_district(filters_dict)
    else:
        result = select_stat_data(filters_dict)

    # 필터 데이터를 서비스 레이어로 전달
    result = select_stat_data(filters_dict)

    return {"statistics_data": result}