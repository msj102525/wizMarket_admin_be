from typing import List
from fastapi import HTTPException

from app.schemas.common_information import CommonInformationOutput
from app.crud.common_information import (
    get_all_report_common_information as crud_get_all_report_common_information,
)


def get_all_report_common_information() -> List[CommonInformationOutput]:
    results = []
    results = crud_get_all_report_common_information()
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results
