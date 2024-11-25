from app.schemas.loc_store import LocStoreInfoForContentOutPut
from app.service.population import *
from app.db.connect import *
from app.crud.loc_store import (
    select_loc_store_for_content_by_store_business_number as crud_select_loc_store_for_content_by_store_business_number,
)
from app.crud.loc_store import *


# 서비스 레이어 함수
async def filter_loc_store(filters):

    data, total_items = get_filtered_loc_store(
        filters.dict()
    )  # 필터 데이터를 딕셔너리로 전달

    return data, total_items


def select_loc_store_for_content_by_store_business_number(
    store_business_number: str,
) -> LocStoreInfoForContentOutPut:

    results = crud_select_loc_store_for_content_by_store_business_number(
        store_business_number
    )
    if not results:
        raise HTTPException(status_code=404, detail="report loc_info not found")
    return results
