from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.biz_sub_category import BizSubCategoryOutput
from service.biz_sub_category import (
    get_all_biz_sub_category_by_biz_main_category_id as service_get_all_biz_sub_category_by_biz_main_category_id,
)

router = APIRouter()


@router.get("", response_model=List[BizSubCategoryOutput])
def get_all_biz_sub_category_by_biz_main_category_id(
    biz_main_category_id: int = Query(True),
):
    try:
        results = service_get_all_biz_sub_category_by_biz_main_category_id(
            biz_main_category_id
        )
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
