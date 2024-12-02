from fastapi import APIRouter, HTTPException
from app.service.loc_info import (
    get_init_stat_data,
    get_init_corr_data,
    select_info_list as service_select_info_list,
    select_stat_data,
    select_stat_data_by_city,
    select_stat_data_by_district,
    select_stat_data_by_sub_district,
    select_nation_j_score,
    select_loc_info_data_date as service_select_loc_info_data_date
)
from app.schemas.loc_info import *
from fastapi import Request
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/select/init/stat/corr")
async def init_data():
    init_stat_data = get_init_stat_data()
    init_all_corr_matrix = get_init_corr_data()

    return {"init_all_corr" : init_all_corr_matrix, "init_stat_data":init_stat_data} 

@router.post("/select/list")
async def filter_data(filters: FilterRequest):
    # 1. 기본 입지분성 값, 상관 분석 값 조회
    filters_dict = filters.dict(exclude_unset=True)

    if filters_dict.get('isLikeSearch') == False :
        # 필터 데이터를 서비스 레이어로 전달
        result, filter_corr_matrix = service_select_info_list(filters_dict)

        # 2. 필터에 따른 J-Score 조회
        city = filters_dict.get('city')
        district = filters_dict.get('district')
        sub_district = filters_dict.get('subDistrict')
        
        # 2-1. 전국 범위 J-Score 조회
        if city is None:
            stat_by_region = select_stat_data(filters_dict)
        # 2-2. 시/도 범위 J-Score 조회
        elif district is None:
            stat_by_region = select_stat_data_by_city(filters_dict)
        # 2-3. 시/군/구 범위 J-Score 조회
        elif sub_district is None:
            stat_by_region = select_stat_data_by_district(filters_dict)
        else:
            stat_by_region = select_stat_data_by_sub_district(filters_dict)
        
        nation_j_score = select_nation_j_score(filters_dict)

        return {"filtered_data": result, "filter_corr" : filter_corr_matrix, "stat_by_region":stat_by_region, "nation_j_score":nation_j_score}
    
    else :
        # 필터 데이터를 서비스 레이어로 전달
        result, base_data = service_select_info_list(filters_dict)

        stat_by_region = select_stat_data(filters_dict)
        
        nation_j_score = select_nation_j_score(filters_dict)

        return {"filtered_data": result, "base_data":base_data, "stat_by_region":stat_by_region, "nation_j_score":nation_j_score}

# 기준 날짜 조회
@router.get("/data/date")
def select_loc_info_data_date() -> List[LocInfoDataDate]:
    try:
        return service_select_loc_info_data_date()

    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex

    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)