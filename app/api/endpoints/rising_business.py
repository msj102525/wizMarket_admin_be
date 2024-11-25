from datetime import date
import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.rising_business import RisingBusinessDataDate, RisingBusinessOutput
from app.service.rising_business import (
    select_all_rising_business_by_dynamic_query as service_select_all_rising_business_by_dynamic_query,
    select_rising_business_data_date as service_select_rising_business_data_date,
)

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/rb", response_model=List[RisingBusinessOutput])
def select_all_rising_business_by_dynamic_query(
    search_cate: Optional[str] = Query(None),
    city_id: Optional[int] = Query(None),
    district_id: Optional[int] = Query(None),
    sub_district_id: Optional[int] = Query(None),
    biz_main_category_id: Optional[int] = Query(None),
    biz_sub_category_id: Optional[int] = Query(None),
    biz_detail_category_id: Optional[int] = Query(None),
    growth_rate_min: Optional[float] = Query(None),
    growth_rate_max: Optional[float] = Query(None),
    rank_min: Optional[int] = Query(None),
    rank_max: Optional[int] = Query(None),
    y_m: Optional[date] = Query(None),
):
    try:
        results = service_select_all_rising_business_by_dynamic_query(
            search_cate=search_cate,
            city_id=city_id,
            district_id=district_id,
            sub_district_id=sub_district_id,
            biz_main_category_id=biz_main_category_id,
            biz_sub_category_id=biz_sub_category_id,
            biz_detail_category_id=biz_detail_category_id,
            growth_rate_min=growth_rate_min,
            growth_rate_max=growth_rate_max,
            rank_min=rank_min,
            rank_max=rank_max,
            y_m=y_m
        )
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/date")
def select_rising_business_data_date() -> List[RisingBusinessDataDate]:
    try:
        return service_select_rising_business_data_date()

    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex

    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

