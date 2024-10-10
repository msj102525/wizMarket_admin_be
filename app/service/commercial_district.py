from typing import List, Optional

from fastapi import HTTPException

from app.crud.city import get_or_create_city_id
from app.crud.commercial_district import (
    select_all_commercial_district_by_sub_district_id,
    select_commercial_district_by_dynamic_query as crud_select_commercial_district_by_dynamic_query,
)

from app.crud.district import get_district_id
from app.crud.sub_district import get_sub_district_id_by
from app.schemas.commercial_district import (
    CommercialDistrictOutput,
)


def get_all_commercial_district_by_sub_district_id(
    city: str, district: str, sub_district: str
) -> List[CommercialDistrictOutput]:
    city_id = get_or_create_city_id(city)
    if city_id <= 0:
        raise HTTPException(status_code=404, detail="City not found")

    district_id = get_district_id(city_id, district)
    if district_id <= 0:
        raise HTTPException(status_code=404, detail="District not found")

    sub_district_id = get_sub_district_id_by(city_id, district_id, sub_district)
    if sub_district_id <= 0:
        raise HTTPException(status_code=404, detail="Sub-district not found")
    else:
        return select_all_commercial_district_by_sub_district_id(sub_district_id)


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
    employee_cost_min: Optional[int] = None, # 인건비X -> 평균 결제
    employee_cost_max: Optional[int] = None, # 인건비X -> 평균 결제
    rental_cost_min: Optional[int] = None,
    rental_cost_max: Optional[int] = None,
    avg_profit_min: Optional[int] = None,
    avg_profit_max: Optional[int] = None,
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
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
