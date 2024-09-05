from fastapi import HTTPException

from app.crud.biz_main_category import (
    get_all_main_category as crud_get_all_main_category,
)


def get_all_biz_main_category():
    results = []
    results = crud_get_all_main_category()
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results
