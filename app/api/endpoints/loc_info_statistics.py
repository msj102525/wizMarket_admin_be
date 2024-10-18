from fastapi import APIRouter, HTTPException
from app.service.statistics import *
from app.schemas.loc_info import *
from fastapi import Request


router = APIRouter()



@router.post("/loc_info_statistics")
async def filter_data(filters: FilterRequest):
    # 입력된 값만 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)

    city = filters_dict.get('city')
    district = filters_dict.get('district')
    sub_district = filters_dict.get('subDistrict')

    if city is None:
        region_stat = select_stat_data(filters_dict)
    elif district is None:
        region_stat = select_stat_data_by_city(filters_dict)
    elif sub_district is None:
        region_stat = select_stat_data_by_district(filters_dict)
    else:
        region_stat = select_stat_data(filters_dict)

    # 1. 전국 범위 j_score 값 조회
    nation_stat = select_stat_data(filters_dict)

    return {"statistics_data": nation_stat}