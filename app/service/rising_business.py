from datetime import date
import logging
from typing import List, Optional
from fastapi import HTTPException

from app.crud.biz_detail_category import (
    get__all_biz_categories_id_like_biz_detail_category_name as crud_get__all_biz_categories_id_like_biz_detail_category_name,
)
from app.crud.rising_business import (
    select_all_rising_business_by_dynamic_query as crud_select_all_rising_business_by_dynamic_query,
    select_rising_business_data_date as crud_select_rising_business_data_date,
)
from app.schemas.rising_business import (
    RisingBusinessDataDate,
    RisingBusinessOutput,
)

logger = logging.getLogger(__name__)


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
    y_m: Optional[date] = None,
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
                        y_m=y_m,
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
            y_m=y_m,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_rising_business_data_date() -> List[RisingBusinessDataDate]:

    try:

        # logger.info(f"detail_category_id_list: {detail_category_id_list}")

        return crud_select_rising_business_data_date()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service RisingBusinessDataDate Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service RisingBusinessDataDate Error: {str(e)}",
        )
