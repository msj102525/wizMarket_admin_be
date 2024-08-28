# from fastapi import APIRouter, HTTPException
# from typing import List
# from app.crud.city import select_region_id_by_city_sub_district
# from app.crud.rising_business import select_all_rising_business_by_region_id
# from app.schemas.rising_business import RisingBusiness


# router = APIRouter()


# @router.get("/", response_model=List[RisingBusiness])
# def get_commercial_district(city: str, sub_district: str):
#     print(city, sub_district)
#     try:
#         region_id = select_region_id_by_city_sub_district(city, sub_district)
#         if region_id:
#             print(region_id)
#             return select_all_rising_business_by_region_id(region_id)
#         else:
#             raise HTTPException(status_code=404, detail="No data found")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
