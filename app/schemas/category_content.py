from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime 
from fastapi import UploadFile, File

class CategoryContentList(BaseModel):
    biz_detail_category_content_id: int
    detail_category_id: int
    status: str
    title :str
    content :str
    created_at:datetime  

    class Config:
        from_attributes = True

class CategoryImageList(BaseModel):
    biz_detail_category_content_image_id: Optional[int] = None
    biz_detail_category_content_id: Optional[int] = None
    biz_detail_category_content_image_url: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryContentListOutPut(BaseModel):
    biz_detail_category_content_id: int
    detail_category_id: int
    status: str
    title :str
    content :str
    created_at:datetime  
    biz_detail_category_content_image_id: Optional[int] = None
    biz_detail_category_content_image_url: Optional[str] = None

    class Config:
        from_attributes = True

# 업종 조회
class CategoryBizCategoryList(BaseModel):
    biz_detail_category_id: int
    biz_main_category_name:str
    biz_sub_category_name:str
    biz_detail_category_name: str


    class Config:
        from_attributes = True

class BizCategoryNumberListRequest(BaseModel):
    biz_category_number_list: List[int]

    class Config:
        from_attributes = True


# 게시 상태 여부 업데이트
class UpdatePublishStatusRequest(BaseModel):
    biz_detail_category_content_id: int
    status: str

    class Config:
        from_attributes = True


# 글 상세 조회
class CategoryDetailRequest(BaseModel):
    biz_detail_category_content_id: int
    
    class Config:
        from_attributes = True

class CategoryDetailContent(BaseModel):
    biz_detail_category_content_id: int
    title: str
    content: str
    status: str

    class Config:
        form_mode = True

class CategoryImage(BaseModel):
    biz_detail_category_content_image_url: str

    class Config:
        from_attributes = True


class CategoryDetailContentResponse(BaseModel):
    category_detail_content: CategoryDetailContent
    image: List[CategoryImage]

    class Config:
        from_attributes = True



# 게시글 수정용
class LocStoreUpdateRequest(BaseModel):
    local_store_content_id: int  # 업데이트할 항목의 ID
    title: str
    content: str
    existing_images: List[str]  # 기존 이미지 파일 경로 또는 파일명
    new_images: Optional[List[UploadFile]] = File(None) 