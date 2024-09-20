from typing import List, Optional

from fastapi import HTTPException

from app.schemas.category import CategoryListOutput
from app.crud.biz_detail_category import (
    select_all_biz_category_by_dynamic_query as crud_select_all_biz_category_by_dynamic_query,
)
from app.crud.classification import (
    select_all_classification_category_by_dynamic_query as crud_select_all_classification_category_by_dynamic_query,
)
from app.crud.business_area_category import (
    select_all_b_a_c_category_by_dynamic_query as crud_select_all_b_a_c_category_by_dynamic_query,
)


def select_all_biz_category_by_dynamic_query(
    main_category_id: Optional[str] = None,
    sub_category_id: Optional[int] = None,
    detail_category_id: Optional[int] = None,
) -> List[CategoryListOutput]:
    try:
        return crud_select_all_biz_category_by_dynamic_query(
            main_category_id, sub_category_id, detail_category_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_all_classification_category_by_dynamic_query(
    main_category_code: Optional[str] = None,
    sub_category_code: Optional[str] = None,
    detail_category_code: Optional[str] = None,
) -> List[CategoryListOutput]:
    try:
        return crud_select_all_classification_category_by_dynamic_query(
            main_category_code,
            sub_category_code,
            detail_category_code,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def select_all_b_a_c_category_by_dynamic_query(
    main_category_code: Optional[str] = None,
    sub_category_code: Optional[str] = None,
    detail_category_code: Optional[str] = None,
) -> List[CategoryListOutput]:
    try:
        return crud_select_all_b_a_c_category_by_dynamic_query(
            main_category_code,
            sub_category_code,
            detail_category_code,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
