from fastapi import APIRouter, HTTPException
from app.service.loc_store import *
from app.schemas.loc_store import *
from fastapi import Request


router = APIRouter()



# 엔드포인트
@router.post("/select_loc_store")
async def filter_data(
    filters: FilterRequest, 
    page: int = 1,  # 페이지 번호, 기본값 1
    limit: int = 20,  # 페이지당 아이템 수, 기본값 20
    sort_by: Optional[str] = None,  # 정렬 기준 (예: 'name', 'location')
    order: Optional[str] = "asc"  # 정렬 순서, 기본값 오름차순
):
    # 필터 값 딕셔너리로 변환
    filters_dict = filters.dict(exclude_unset=True)
    
    # 예시로 필터 데이터를 서비스 레이어에 전달
    result = await filter_location_store(filters_dict, page=page, limit=limit, sort_by=sort_by, order=order)
    print(type(result))
    # 임시 응답
    return {"filtered_data", result}  # 실제로는 데이터베이스에서 조회한 결과를 반환