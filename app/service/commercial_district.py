from datetime import date
import logging
from typing import List, Optional

from fastapi import HTTPException

from app.crud.city import get_or_create_city_id
from app.crud.commercial_district import (
    select_commercial_district_by_dynamic_query as crud_select_commercial_district_by_dynamic_query,
    select_commercial_district_data_date as crud_select_commercial_district_data_date,
)

from app.crud.district import get_district_id
from app.crud.sub_district import get_sub_district_id_by
from app.schemas.commercial_district import (
    CommercialDistrictOutput,
    CommercialStatisticsDataDate,
)

logger = logging.getLogger(__name__)


def select_commercial_district_by_dynamic_query(
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    sub_district_id: Optional[int] = None,
    biz_main_category_id: Optional[int] = None,
    biz_sub_category_id: Optional[int] = None,
    biz_detail_category_id: Optional[int] = None,
    market_size_min: Optional[int] = None,
    market_size_max: Optional[int] = None,
    avg_sales_min: Optional[int] = None,
    avg_sales_max: Optional[int] = None,
    operating_cost_min: Optional[int] = None,
    operating_cost_max: Optional[int] = None,
    food_cost_min: Optional[int] = None,
    food_cost_max: Optional[int] = None,
    employee_cost_min: Optional[int] = None,  # 인건비X -> 평균 결제
    employee_cost_max: Optional[int] = None,  # 인건비X -> 평균 결제
    rental_cost_min: Optional[int] = None,
    rental_cost_max: Optional[int] = None,
    avg_profit_min: Optional[int] = None,
    avg_profit_max: Optional[int] = None,
    y_m: Optional[date] = None,
) -> List[CommercialDistrictOutput]:
    try:
        return crud_select_commercial_district_by_dynamic_query(
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_commercial_district_data_date() -> List[CommercialStatisticsDataDate]:

    try:

        # logger.info(f"detail_category_id_list: {detail_category_id_list}")

        return crud_select_commercial_district_data_date()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service CommercialStatisticsDataDate Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service CommercialStatisticsDataDate Error: {str(e)}",
        )
