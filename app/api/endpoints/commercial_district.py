from datetime import date
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.schemas.commercial_district import (
    CommercialDistrictOutput,
    CommercialStatisticsData,
    CommercialStatisticsDataDate,
    CommercialStatisticsOutput,
)
from app.service.commercial_district import (
    select_commercial_district_by_dynamic_query as service_select_commercial_district_by_dynamic_query,
    select_commercial_district_data_date as service_select_commercial_district_data_date,
)
from app.service.statistics import (
    select_statistics_by_sub_district_detail_category_new as service_select_statistics_by_sub_district_detail_category_new,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/cd", response_model=List[CommercialStatisticsOutput])
def get_commercial_district_by_query(
    city_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    sub_district_id: Optional[int] = Query(None),
    biz_main_category_id: Optional[int] = Query(None),
    biz_sub_category_id: Optional[int] = Query(None),
    biz_detail_category_id: Optional[int] = Query(None),
    market_size_min: Optional[int] = Query(None),
    market_size_max: Optional[int] = Query(None),
    avg_sales_min: Optional[int] = Query(None),
    avg_sales_max: Optional[int] = Query(None),
    operating_cost_min: Optional[int] = Query(None),
    operating_cost_max: Optional[int] = Query(None),
    food_cost_min: Optional[int] = Query(None),
    food_cost_max: Optional[int] = Query(None),
    employee_cost_min: Optional[int] = Query(None),  # 인건비X -> 평균 결제
    employee_cost_max: Optional[int] = Query(None),  # 인건비X -> 평균 결제
    rental_cost_min: Optional[int] = Query(None),
    rental_cost_max: Optional[int] = Query(None),
    avg_profit_min: Optional[int] = Query(None),
    avg_profit_max: Optional[int] = Query(None),
    y_m: Optional[date] = Query(None),
):
    try:
        # logger.info(f"y_m:{y_m}")

        results: CommercialDistrictOutput = (
            service_select_commercial_district_by_dynamic_query(
                city_id,
                district_id,
                sub_district_id,
                biz_main_category_id,
                biz_sub_category_id,
                biz_detail_category_id,
                market_size_min,
                market_size_max,
                avg_sales_min,
                avg_sales_max,
                operating_cost_min,
                operating_cost_max,
                food_cost_min,
                food_cost_max,
                employee_cost_min,
                employee_cost_max,
                rental_cost_min,
                rental_cost_max,
                avg_profit_min,
                avg_profit_max,
                y_m,
            )
        )

        # 결과와 통계 데이터를 결합하여 반환할 리스트
        combined_results = []

        for item in results:
            # 각 상권의 통계 데이터 가져오기
            statistics_data: CommercialStatisticsData = (
                service_select_statistics_by_sub_district_detail_category_new(
                    item.city_name,
                    item.district_name,
                    item.sub_district_name,
                    item.biz_detail_category_name,
                    item.y_m,
                )
            )

            # 결과와 통계 데이터를 결합
            combined_results.append(
                CommercialStatisticsOutput(
                    commercial_district_data=item,
                    statistics_data=statistics_data,
                )
            )

        return combined_results

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/date")
def select_commercial_district_data_date() -> List[CommercialStatisticsDataDate]:
    try:
        return service_select_commercial_district_data_date()

    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex

    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
