from typing import List
from fastapi import HTTPException

from app.crud.reference import get_all_reference as crud_get_all_reference
from app.schemas.reference import Reference


def get_all_reference() -> List[Reference]:
    results = crud_get_all_reference()
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results
