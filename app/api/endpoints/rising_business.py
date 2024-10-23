from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.rising_business import RisingBusinessOutput
from app.service.rising_business import (
    get_all_rising_business_by_region_name,
    select_all_rising_business_by_dynamic_query as service_select_all_rising_business_by_dynamic_query,
)


router = APIRouter()


@router.get("", response_model=List[RisingBusinessOutput])
def get_rising_business(city: str, district: str, sub_district: str):
    # print(f"city: {city}, district: {district}, sub_d: {sub_district}")
    try:
        results = get_all_rising_business_by_region_name(city, district, sub_district)
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        )
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
