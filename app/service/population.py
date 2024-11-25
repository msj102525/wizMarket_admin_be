from fastapi import HTTPException
from app.crud.population import *
from app.crud.statistics import (
    select_nationwide_jscore_by_stat_item_id_and_sub_district_id as crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id,
    select_state_item_id,
)
from app.schemas.loc_info import LocationInfoReportOutput
from app.schemas.loc_store import LocalStoreSubdistrict
from app.schemas.population import PopulationJScoreOutput, PopulationDataDate
from app.schemas.statistics import LocStatisticsOutput
from app.db.connect import *
from app.crud.population import (
    get_latest_population_data_by_subdistrict_id as crud_get_latest_population_data_by_subdistrict_id,
    select_population_data_date as crud_select_population_data_date
)
from app.crud.loc_store import (
    select_loc_info_report_data_by_sub_district_id as crud_select_loc_info_report_data_by_sub_district_id,
)
import logging

logger = logging.getLogger(__name__)

# 상세 조회
async def filter_population_data(filters: dict):
    # print("서비스 전")
    try:
        # select/population.py의 쿼리 함수 호출
        results = get_filtered_population_data(filters)
        return results
    except Exception as e:
        raise Exception(f"Error in filtering population data: {str(e)}")


# 엑셀 다운
async def download_data(filters: dict):
    try:
        results = download_data_ex(filters)
        # print("엑셀 다운 로드 후")
        return results
    except Exception as e:
        raise Exception(f"Error in filtering population data: {str(e)}")


# 기준 날짜 조회
def select_population_data_date() -> List[PopulationDataDate]:
    try:
        # logger.info(f"detail_category_id_list: {detail_category_id_list}")
        return crud_select_population_data_date()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service PopulationDataDate Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service PopulationDataDate Error: {str(e)}",
        )

def select_report_population_by_store_business_number(
    store_business_id: str,
) -> PopulationJScoreOutput:
    try:
        local_store_sub_district_data: LocalStoreSubdistrict = (
            crud_select_local_store_sub_distirct_id_by_store_business_number(
                store_business_id
            )
        )

        sub_district_id = local_store_sub_district_data.get("SUB_DISTRICT_ID")

        if sub_district_id is None:
            raise HTTPException(status_code=404, detail="Sub-district ID not found.")

        # 최신 인구 데이터 조회
        population_data = crud_get_latest_population_data_by_subdistrict_id(
            sub_district_id
        )

        # 통계 항목 ID 조회
        resident_stat_item_id: int = select_state_item_id("loc_info", "resident")
        work_pop_stat_item_id: int = select_state_item_id("loc_info", "work_pop")
        house_stat_item_id: int = select_state_item_id("loc_info", "house")
        shop_stat_item_id: int = select_state_item_id("loc_info", "shop")
        income_stat_item_id: int = select_state_item_id("loc_info", "income")

        # J-score 조회 및 반올림 처리
        resident_jscore: float = round(
            crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                resident_stat_item_id, sub_district_id
            ).get("J_SCORE"),
            1,
        )
        work_pop_jscore: float = round(
            crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                work_pop_stat_item_id, sub_district_id
            ).get("J_SCORE"),
            1,
        )
        house_jscore: float = round(
            crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                house_stat_item_id, sub_district_id
            ).get("J_SCORE"),
            1,
        )
        shop_jscore: float = round(
            crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                shop_stat_item_id, sub_district_id
            ).get("J_SCORE"),
            1,
        )
        income_jscore: float = round(
            crud_select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                income_stat_item_id, sub_district_id
            ).get("J_SCORE"),
            1,
        )

        j_score_data = LocStatisticsOutput(
            resident_jscore=resident_jscore,
            work_pop_jscore=work_pop_jscore,
            house_jscore=house_jscore,
            shop_jscore=shop_jscore,
            income_jscore=income_jscore,
        )

        loc_info_data: LocationInfoReportOutput = (
            crud_select_loc_info_report_data_by_sub_district_id(sub_district_id)
        )

        population_j_score_data = PopulationJScoreOutput(
            population_data=population_data,
            j_score_data=j_score_data,
            loc_info_data=loc_info_data,
        )

        return population_j_score_data
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
