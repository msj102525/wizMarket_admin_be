from typing import List
from fastapi import HTTPException
from app.schemas.biz_sub_category import BizSubCategoryOutPut
from crud.biz_detail_category import (
    get_all_biz_detail_category_by_biz_sub_category_id as crud_get_all_biz_detail_category_by_biz_sub_category_id,
)


def get_all_biz_sub_category_by_biz_main_category_id(
    biz_sub_category_id: int,
) -> List[BizSubCategoryOutPut]:
    results = []
    results = crud_get_all_biz_detail_category_by_biz_sub_category_id(
        biz_sub_category_id
    )
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results
