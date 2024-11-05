from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime 
from fastapi import UploadFile, File

class LocStoreContentList(BaseModel):
    local_store_content_id: int
    store_business_number: str
    store_name:str
    road_name:str
    status: str
    title :str
    content :str
    created_at:datetime  

    class Config:
        from_attributes = True

class LocStoreCategoryList(BaseModel):
    store_business_number: str
    large_category_name:str
    medium_category_name:str
    small_category_name: str

    class Config:
        from_attributes = True

# 업종 조회
class StoreBusinessNumberListRequest(BaseModel):
    store_business_number_list: List[str]

    class Config:
        from_attributes = True

# 게시 상태 여부 업데이트
class UpdatePublishStatusRequest(BaseModel):
    local_store_content_id: int
    status: str

    class Config:
        from_attributes = True


# 글 상세 조회
class LocStoreDetailRequest(BaseModel):
    local_store_content_id: int
    
    class Config:
        from_attributes = True

class LocStoreDetailContent(BaseModel):
    local_store_content_id: int
    title: str
    content: str
    status: str

    class Config:
        form_mode = True

class LocStoreImage(BaseModel):
    local_store_image_url: str

    class Config:
        from_attributes = True


class LocStoreDetailContentResponse(BaseModel):
    local_store_detail_content: LocStoreDetailContent
    image: List[LocStoreImage]

    class Config:
        from_attributes = True


# 게시글 수정용
class LocStoreUpdateRequest(BaseModel):
    local_store_content_id: int  # 업데이트할 항목의 ID
    title: str
    content: str
    existing_images: List[str]  # 기존 이미지 파일 경로 또는 파일명
    new_images: Optional[List[UploadFile]] = File(None) 