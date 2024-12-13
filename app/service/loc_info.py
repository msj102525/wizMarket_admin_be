from fastapi import HTTPException
from datetime import date
from app.crud.loc_info import *
from app.crud.loc_info import (
    select_stat_data_avg,
    get_all_corr,
    select_info_list as crud_select_info_list,
    get_filter_corr,
    get_stat_data,
    get_stat_data_by_city,
    get_stat_data_by_distirct,
    get_stat_data_by_sub_distirct,
    get_nation_j_score,
    select_loc_info_data_date as crud_select_loc_info_data_date,
    select_info_list_similar as crud_select_info_list_similar 
)
import pandas as pd
from app.crud.statistics import (
    select_nationwide_jscore_by_stat_item_id_and_sub_district_id as crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id,
    select_state_item_id as crud_select_state_item_id,
)
from app.schemas.loc_store import LocalStoreSubdistrict
from app.schemas.statistics import DataRefDateSubDistrictName, LocInfoStatisticsDataRefOutput, LocInfoStatisticsOutput
from typing import List, Optional
from app.schemas.loc_info import LocInfoDataDate
import logging

logger = logging.getLogger(__name__)

def get_init_stat_data():
    result = select_stat_data_avg()
    return result

def get_init_corr_data():
    years = ['2024-08-01', '2024-10-01', '2024-11-01']

    # 년도별로 결과를 저장하기 위한 딕셔너리
    all_corr_matrices = {}

    for year in years:
        # 해당 날짜의 데이터를 가져옴
        all_corr = get_all_corr(year)

        # 필요한 항목들로 DataFrame 생성 (SALES와 다른 변수들)
        df_all = pd.DataFrame(
            all_corr,
            columns=[
                "SALES",
                "SHOP",
                "MOVE_POP",
                "WORK_POP",
                "INCOME",
                "SPEND",
                "HOUSE",
                "RESIDENT",
                "APART_PRICE"
            ],
        )
        

        # 전국 상관분석 수행
        all_corr_matrix = df_all.corr().fillna('-')  # NaN 값을 '-'로 대체
        all_corr_matrix_dict = all_corr_matrix.to_dict()
        # 년도별 상관분석 결과를 저장
        all_corr_matrices[year] = all_corr_matrix_dict


    return all_corr_matrices

def select_info_list(filters: dict):
    if filters.get('isLikeSearch') == False :
        # 필터링 로직: 필요하면 여기서 추가적인 필터 처리를 할 수 있습니다.
        filtered_locations = crud_select_info_list(filters)

        # 상관 분석 처리
        years = ['2024-08-01', '2024-10-01', '2024-11-01']

        # 년도별로 결과를 저장하기 위한 딕셔너리
        filter_corr_matrices = {}

        for year in years:
            # 해당 날짜의 데이터를 가져옴

            # 지역 내 상관 분석
            filter_corr = get_filter_corr(filters, year)

            # 지역 내 분석 수행
            df_filter = pd.DataFrame(filter_corr)

            filter_corr_matrix = df_filter.groupby("DISTRICT_NAME")[
                [
                    "SALES",
                    "SHOP",
                    "MOVE_POP",
                    "WORK_POP",
                    "INCOME",
                    "SPEND",
                    "HOUSE",
                    "RESIDENT",
                    "APART_PRICE"
                ]
            ].corr()
            
            # NaN 값을 '-'로 대체
            filter_corr_matrix = filter_corr_matrix.fillna('-')

            # 년도별 지역 내 상관분석 결과를 저장
            filter_corr_matrix = filter_corr_matrix.reset_index().to_dict(orient="records")
            filter_corr_matrices[year] = filter_corr_matrix


        # 필요 시 추가적인 비즈니스 로직을 처리할 수 있음
        return filtered_locations, filter_corr_matrices

    else :
        filtered_locations, base_data = crud_select_info_list_similar(filters)
    return filtered_locations, base_data


# 추가 j_score 로직 변경


def select_stat_data(filters_dict):
    result = get_stat_data(filters_dict)
    return result

def select_stat_data_by_city(filters_dict):
    result = get_stat_data_by_city(filters_dict)
    return result

def select_stat_data_by_district(filters_dict):
    result = get_stat_data_by_distirct(filters_dict)
    return result

def select_stat_data_by_sub_district(filters_dict):
    result = get_stat_data_by_sub_distirct(filters_dict)
    return result

def select_nation_j_score(filters_dict):
    result = get_nation_j_score(filters_dict)
    return result


# 기준 날짜 조회
def select_loc_info_data_date() -> List[LocInfoDataDate]:
    try:
        return crud_select_loc_info_data_date()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service LocInfoDataDate Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service LocInfoDataDate Error: {str(e)}",
        )


