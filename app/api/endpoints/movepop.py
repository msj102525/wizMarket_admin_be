from fastapi import APIRouter, HTTPException
from app.service.movepop import process_keywords_from_excel

router = APIRouter()

@router.post('/start-crawl')
async def start_crawl():
    try:
        print("Starting process_keywords_from_excel")
        await process_keywords_from_excel()  # await를 사용하여 비동기 함수 호출
        print("Finished process_keywords_from_excel")
        return {"message": "크롤링이 성공적으로 완료되었습니다."}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"크롤링에 실패했습니다. {e}")
