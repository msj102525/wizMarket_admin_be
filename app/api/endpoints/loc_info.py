from fastapi import APIRouter, HTTPException
from app.service.loc_info import *
from app.schemas.loc_info import *
from fastapi import Request


router = APIRouter()



@router.post("/select_loc_info")
async def filter_data(filters: FilterRequest):
    # 1. 기본 입지분성 값, 상관 분석 값 조회
    filters_dict = filters.dict(exclude_unset=True)
    # 필터 데이터를 서비스 레이어로 전달
    result, all_corr_matrix, filter_corr_matrix = filter_location_info(filters_dict)

    # 2. 필터에 따른 J-Score 조회
    city = filters_dict.get('city')
    district = filters_dict.get('district')
    sub_district = filters_dict.get('subDistrict')

    # 2-1. 전국 범위 J-Score 조회
    if city is None:
        region_stat = select_stat_data(filters_dict)
    # 2-2. 시/도 범위 J-Score 조회
    elif district is None:
        region_stat = select_stat_data_by_city(filters_dict)
    # 2-3. 시/군/구 범위 J-Score 조회
    elif sub_district is None:
        region_stat = select_stat_data_by_district(filters_dict)
    else:
        region_stat = select_stat_data_by_sub_district(filters_dict)

    # 3. 기본 통계값 (전국) 조회
    stat_data = select_stat_data_avg()

    # 4.

    return {"filtered_data": result, "all_corr" : all_corr_matrix, "filter_corr" : filter_corr_matrix, "region_j_score":region_stat, "total_stat":stat_data}