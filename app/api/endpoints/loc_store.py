from fastapi import APIRouter, HTTPException
from app.service.loc_store import (
    filter_loc_store,
    select_loc_store_for_content_by_store_business_number as service_select_loc_store_for_content_by_store_business_number,
    select_download_store_list as service_select_download_store_list
)
from app.schemas.loc_store import *
from fastapi import Request
import logging
from tempfile import NamedTemporaryFile
from fastapi.responses import FileResponse
import pandas as pd
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# 필터로 조회
@router.post("/select/store/list")
def filter_data(filters: FilterRequest):
    # 필터 정보를 서비스 레이어로 전달
    data, total_items = filter_loc_store(filters)

    return {
        "filtered_data": data,     # 페이징된 데이터
        "total_items": total_items  # 총 데이터 개수
    }


# 엑셀 다운
@router.post("/select/download/store/list")
def select_download_store_list(filters: ExcelRequest):
    """
    필터에 따른 데이터를 조회하고 엑셀 파일로 다운로드.
    """
    # 데이터 조회
    try:
        data = service_select_download_store_list(filters)  # 서비스에서 데이터 가져오기
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data fetch error: {str(e)}")

    if not data:
        raise HTTPException(status_code=404, detail="No data found.")

    # 데이터프레임 생성
    df = pd.DataFrame(data)

    # 엑셀 파일 생성
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
        file_path = temp_file.name
        df.to_excel(file_path, index=False, engine="openpyxl")

    today_date = datetime.now().strftime("%Y-%m-%d")
    file_name = f"매장정보_{today_date}.xlsx"

    # 파일 응답
    return FileResponse(
        file_path,
        filename=file_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


    

# 매장 리스트에서 모달창 띄우기
@router.post("/select/init/content", response_model=LocStoreInfoForContentOutPut)
def select_loc_store_for_content_by_store_business_number(store_business_number: str):
    # 쿼리 매개변수로 전달된 store_business_number 값 수신
    try:
        data = service_select_loc_store_for_content_by_store_business_number(store_business_number)
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


