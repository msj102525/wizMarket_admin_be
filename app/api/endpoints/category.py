from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.category import CategoryListOutput
from app.service.category import (
    select_all_biz_category_by_dynamic_query as service_select_all_biz_category_by_dynamic_query,
    select_all_classification_category_by_dynamic_query as service_select_all_classification_category_by_dynamic_query,
    select_all_b_a_c_category_by_dynamic_query as service_select_all_b_a_c_category_by_dynamic_query,
)

router = APIRouter()


@router.get("/biz", response_model=List[CategoryListOutput])
def select_all_biz_category_by_dynamic_query(
    main_category_id: Optional[int] = Query(None),
    sub_category_id: Optional[int] = Query(None),
    detail_category_id: Optional[int] = Query(None),
):

    try:
        results = service_select_all_biz_category_by_dynamic_query(
            main_category_id=main_category_id,
            sub_category_id=sub_category_id,
            detail_category_id=detail_category_id,
        )

        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classification", response_model=List[CategoryListOutput])
def select_all_classification_category_by_dynamic_query(
    main_category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    detail_category_code: Optional[str] = Query(None),
) -> List[CategoryListOutput]:

    try:
        results = service_select_all_classification_category_by_dynamic_query(
            main_category_code,
            sub_category_code,
            detail_category_code,
        )

        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business_area_category", response_model=List[CategoryListOutput])
def select_all_classification_category_by_dynamic_query(
    main_category_code: Optional[str] = Query(None),
    sub_category_code: Optional[str] = Query(None),
    detail_category_code: Optional[str] = Query(None),
) -> List[CategoryListOutput]:

    try:
        results = service_select_all_b_a_c_category_by_dynamic_query(
            main_category_code,
            sub_category_code,
            detail_category_code,
        )

        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
