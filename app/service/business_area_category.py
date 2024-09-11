from app.crud.business_area_category import *

async def get_business_area_category_service(reference_id: int):
    # 비즈니스 로직이 있다면 여기서 처리
    print(f"Service layer received reference_id: {reference_id}")
    
    # CRUD 레이어에 reference_id 전달
    result = get_business_area_category_from_db(reference_id)
    
    return result