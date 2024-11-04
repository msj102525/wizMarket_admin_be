from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime 

class LocStoreContentList(BaseModel):
    local_store_content_id: int
    store_business_number: str
    store_name:str
    road_name:str
    is_publish: bool
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

# 계시 상태 여부 업데이트
class UpdatePublishStatusRequest(BaseModel):
    local_store_content_id: int
    is_publish: bool

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
    is_publish: bool

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