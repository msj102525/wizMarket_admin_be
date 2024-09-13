from typing import List
from fastapi import HTTPException

from app.crud.biz_detail_category import (
    get_all_detail_category_count as crud_biz_get_all_detail_category_count,
)
from app.crud.business_area_category import (
    get_all_detail_category_count as crud_b_a_c_get_all_detail_category_count,
)
from app.crud.classification import (
    get_all_sub_sub_detail_category_count as crud_classification_get_all_detail_category_count,
)
from app.crud.reference import get_all_reference as crud_get_all_reference
from app.schemas.reference import Reference, ReferenceCategoryCountOutput


def get_all_reference() -> List[ReferenceCategoryCountOutput]:
    results: List[ReferenceCategoryCountOutput] = []

    # Fetch category counts
    biz_category_count = crud_biz_get_all_detail_category_count()
    classification_category_count = crud_classification_get_all_detail_category_count()
    business_area_category_count = crud_b_a_c_get_all_detail_category_count()

    rows = crud_get_all_reference()
    print(rows)

    for row in rows:
        reference_id = row.reference_id
        reference_name = row.reference_name

        if reference_id == 1:
            category_count = biz_category_count
        elif reference_id == 2:
            category_count = classification_category_count
        elif reference_id == 3:
            category_count = business_area_category_count
        else:
            category_count = 0

        reference_output = ReferenceCategoryCountOutput(
            reference_id=reference_id,
            reference_name=reference_name,
            category_count=category_count,
        )
        results.append(reference_output)

    if not results:
        raise HTTPException(status_code=404, detail="No references found")

    return results


if __name__ == "__main__":
    print(get_all_reference())
