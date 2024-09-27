from typing import List, Optional
from fastapi import HTTPException

from app.crud.biz_detail_category import (
    get__all_biz_categories_id_like_biz_detail_category_name as crud_get__all_biz_categories_id_like_biz_detail_category_name,
)
from app.crud.city import get_or_create_city_id
from app.crud.district import get_district_id
from app.crud.rising_business import (
    select_all_rising_business_by_dynamic_query as crud_select_all_rising_business_by_dynamic_query,
    select_all_rising_business_by_region_id,
    select_top5_rising_business as crud_select_top5_rising_business,
    select_top3_rising_business_by_store_business_number as crud_select_top3_rising_business_by_store_business_number,
)
from app.crud.sub_district import get_sub_district_id_by
from app.schemas.rising_business import (
    RisingBusinessOutput,
)


def get_all_rising_business_by_region_name(
    city: str, district: str, sub_district: str
) -> List[RisingBusinessOutput]:
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
        return select_all_rising_business_by_region_id(
            city_id, district_id, sub_district_id
        )


def select_all_rising_business_by_dynamic_query(
    search_cate: Optional[str] = None,
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    sub_district_id: Optional[int] = None,
    biz_main_category_id: Optional[int] = None,
    biz_sub_category_id: Optional[int] = None,
    biz_detail_category_id: Optional[int] = None,
    growth_rate_min: Optional[float] = None,
    growth_rate_max: Optional[float] = None,
    rank_min: Optional[int] = None,
    rank_max: Optional[int] = None,
) -> List[RisingBusinessOutput]:
    try:
        if search_cate:
            cate_list = crud_get__all_biz_categories_id_like_biz_detail_category_name(
                search_cate
            )

            if cate_list:
                results = []
                for main_cat_id, sub_cat_id, detail_cat_id in cate_list:
                    result = crud_select_all_rising_business_by_dynamic_query(
                        city_id=city_id,
                        district_id=district_id,
                        sub_district_id=sub_district_id,
                        biz_main_category_id=main_cat_id,
                        biz_sub_category_id=sub_cat_id,
                        biz_detail_category_id=detail_cat_id,
                        growth_rate_min=growth_rate_min,
                        growth_rate_max=growth_rate_max,
                        rank_min=rank_min,
                        rank_max=rank_max,
                    )
                    results.extend(result)
                return results
            else:
                return []
        return crud_select_all_rising_business_by_dynamic_query(
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_top5_rising_business() -> List[RisingBusinessOutput]:
    try:
        return crud_select_top5_rising_business()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_top3_rising_business_by_store_business_number(
    store_business_id: str,
) -> List[RisingBusinessOutput]:
    try:
        return crud_select_top3_rising_business_by_store_business_number(store_business_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
