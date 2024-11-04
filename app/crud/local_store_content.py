from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.local_store_content import LocStoreContentList, LocStoreCategoryList, LocStoreDetailContent, LocStoreDetailContentResponse,LocStoreImage

load_dotenv()
logger = logging.getLogger(__name__)

def insert_store_content(store_business_number: str, title: str, content: str):
    # 데이터베이스 연결 설정
    connection = get_db_connection(db_database=os.getenv("DB_REPORT"))
    
    try:
        with connection.cursor() as cursor:
            # 데이터 인서트 쿼리
            insert_query = """
                INSERT INTO LOCAL_STORE_CONTENT 
                (STORE_BUSINESS_NUMBER, TITLE, CONTENT) 
                VALUES (%s, %s, %s)
            """
            # 쿼리 실행
            cursor.execute(insert_query, (store_business_number, title, content))
            # 자동 생성된 PK 가져오기
            pk = cursor.lastrowid
            # 커밋하여 DB에 반영
            commit(connection)
            return pk

    except pymysql.MySQLError as e:
        rollback(connection)  # 오류 시 롤백
        print(f"Database error: {e}")
        raise

    finally:
        close_cursor(cursor)   # 커서 종료
        close_connection(connection)  # 연결 종료



def select_loc_store_content_list():
    connection = get_db_connection(db_database=os.getenv("DB_REPORT"))
    try:
        with connection.cursor() as cursor:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_query = """
                    SELECT 
                        ls.LOCAL_STORE_CONTENT_ID,
                        ls.STORE_BUSINESS_NUMBER,
                        r.STORE_NAME,
                        r.ROAD_NAME,
                        ls.TITLE,
                        ls.CONTENT,
                        ls.IS_PUBLISH,
                        ls.CREATED_AT
                    FROM
                        LOCAL_STORE_CONTENT ls
                    JOIN REPORT r
                    ON r.STORE_BUSINESS_NUMBER = ls.STORE_BUSINESS_NUMBER;
                    """
                # logger.info(f"Executing query: {select_query}")
                cursor.execute(select_query)
                rows = cursor.fetchall()
                if not rows:
                    raise HTTPException(
                        status_code=404,
                        detail=f"LocStoreContentList 해당하는 매장 정보를 찾을 수 없습니다.",
                    )
                result = [
                    LocStoreContentList(
                        local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                        store_business_number=row["STORE_BUSINESS_NUMBER"],
                        store_name = row["STORE_NAME"],
                        road_name = row["ROAD_NAME"],
                        title=row["TITLE"],
                        content=row["CONTENT"],
                        is_publish=bool(row["IS_PUBLISH"]),
                        created_at=row["CREATED_AT"],
                    )
                    for row in rows
                ]
                return result

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    

# 업종 조회
def select_loc_store_category(store_business_number: str):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    STORE_BUSINESS_NUMBER,
                    LARGE_CATEGORY_NAME,
                    MEDIUM_CATEGORY_NAME,
                    SMALL_CATEGORY_NAME
                FROM
                    LOCAL_STORE
                WHERE
                    STORE_BUSINESS_NUMBER = %s
                """
            cursor.execute(select_query, (store_business_number,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"LocStoreCategoryList 해당하는 매장 정보를 찾을 수 없습니다.",
                )

            result = LocStoreCategoryList(
                store_business_number=row["STORE_BUSINESS_NUMBER"],
                large_category_name=row["LARGE_CATEGORY_NAME"],
                medium_category_name=row["MEDIUM_CATEGORY_NAME"],
                small_category_name=row["SMALL_CATEGORY_NAME"]
            )
            return result

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")


# 계시 상태 여부 업데이트
def update_loc_store_is_publish(local_store_content_id: int, is_publish: bool) -> bool:
    connection = get_db_connection(db_database=os.getenv("DB_REPORT"))

    try:
        with connection.cursor() as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE LOCAL_STORE_CONTENT
                SET IS_PUBLISH = %s
                WHERE LOCAL_STORE_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (is_publish, local_store_content_id))
            connection.commit()
            
            # rowcount를 통해 업데이트 성공 여부 확인
            if cursor.rowcount == 0:
                return False  # 업데이트된 행이 없는 경우 False 반환
            return True  # 업데이트 성공 시 True 반환
    except pymysql.MySQLError as e:
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")
    finally:
        connection.close()


# 글 상세 조회
def select_loc_store_for_detail_content(local_store_content_id: int):
    connection = get_db_connection(db_database=os.getenv("DB_REPORT"))
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 첫 번째 쿼리: 매장 기본 정보 조회
            select_content_query = """
                SELECT 
                    LOCAL_STORE_CONTENT_ID,
                    TITLE,
                    CONTENT,
                    IS_PUBLISH
                FROM
                    LOCAL_STORE_CONTENT
                WHERE
                    LOCAL_STORE_CONTENT_ID = %s
            """
            cursor.execute(select_content_query, (local_store_content_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="해당하는 매장 정보를 찾을 수 없습니다."
                )

            # 두 번째 쿼리: 이미지 정보 조회
            select_images_query = """
                SELECT 
                    LOCAL_STORE_CONTENT_IMAGE_URL
                FROM
                    LOCAL_STORE_CONTENT_IMAGE  
                WHERE
                    LOCAL_STORE_CONTENT_ID = %s
            """

            cursor.execute(select_images_query, (local_store_content_id,))
            images = cursor.fetchall()
            image_urls = [LocStoreImage(local_store_image_url=image["LOCAL_STORE_CONTENT_IMAGE_URL"]) for image in images]

            # 결과를 Pydantic 모델 형식에 맞춰 반환
            result = LocStoreDetailContentResponse(
                local_store_detail_content=LocStoreDetailContent(
                    local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                    title=row["TITLE"],
                    content=row["CONTENT"],
                    is_publish=row["IS_PUBLISH"]
                ),
                image=image_urls
            )
         
            return result

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
