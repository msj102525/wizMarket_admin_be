from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.category_content import (
    CategoryContentList, 
    CategoryBizCategoryList, 
    CategoryDetailContent, 
    CategoryDetailContentResponse,
    CategoryImage
)
from typing import Optional, List


load_dotenv()
logger = logging.getLogger(__name__)

def insert_category_content(detail_category: int, title: str, content: str):
    # 데이터베이스 연결 설정
    connection = get_re_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # 데이터 인서트 쿼리
            insert_query = """
                INSERT INTO BIZ_DETAIL_CATEGORY_CONTENT 
                (DETAIL_CATEGORY_ID, TITLE, CONTENT) 
                VALUES (%s, %s, %s)
            """
            # 쿼리 실행
            cursor.execute(insert_query, (detail_category, title, content))
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



def select_category_content_list():
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    BIZ_DETAIL_CATEGORY_CONTENT_ID,
                    DETAIL_CATEGORY_ID,
                    TITLE,
                    CONTENT,
                    STATUS,
                    CREATED_AT
                FROM
                    BIZ_DETAIL_CATEGORY_CONTENT
                WHERE STATUS != 'D';

            """
            cursor.execute(select_query)
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="CategoryContentList 해당하는 업종 정보를 찾을 수 없습니다.",
                )
            result = [
                CategoryContentList(
                    biz_detail_category_content_id = row["BIZ_DETAIL_CATEGORY_CONTENT_ID"],
                    detail_category_id = row["DETAIL_CATEGORY_ID"],
                    title=row["TITLE"],
                    content=row["CONTENT"],
                    status=row["STATUS"],
                    created_at=row["CREATED_AT"],
                )
                for row in rows
            ]
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred CategoryContentList: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기



# 업종 조회
def select_category_biz_category(biz_category_number: int):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    main.BIZ_MAIN_CATEGORY_NAME AS BIZ_MAIN_CATEGORY_NAME,
                    sub.BIZ_SUB_CATEGORY_NAME AS BIZ_SUB_CATEGORY_NAME,
                    detail.BIZ_DETAIL_CATEGORY_NAME AS BIZ_DETAIL_CATEGORY_NAME,
                    detail.BIZ_DETAIL_CATEGORY_ID AS BIZ_DETAIL_CATEGORY_ID
                FROM
                    BIZ_DETAIL_CATEGORY AS detail
                JOIN
                    BIZ_SUB_CATEGORY AS sub ON detail.BIZ_SUB_CATEGORY_ID = sub.BIZ_SUB_CATEGORY_ID
                JOIN
                    BIZ_MAIN_CATEGORY AS main ON sub.BIZ_MAIN_CATEGORY_ID = main.BIZ_MAIN_CATEGORY_ID
                WHERE
                    detail.BIZ_DETAIL_CATEGORY_ID = %s
                """
            cursor.execute(select_query, (biz_category_number,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="CategoryBizCategoryList에 해당하는 매장 정보를 찾을 수 없습니다.",
                )

            # Pydantic 모델에 맞춰 데이터 반환
            result = CategoryBizCategoryList(
                biz_main_category_name=row["BIZ_MAIN_CATEGORY_NAME"],
                biz_sub_category_name=row["BIZ_SUB_CATEGORY_NAME"],
                biz_detail_category_name=row["BIZ_DETAIL_CATEGORY_NAME"],
                biz_detail_category_id=row["BIZ_DETAIL_CATEGORY_ID"]
            )
            return result

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred in CategoryBizCategoryList: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)



# 게시 상태 여부 업데이트
def update_category_content_status(biz_detail_category_content_id: int, status: str) -> bool:
    connection = get_re_db_connection()

    try:
        with connection.cursor() as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE BIZ_DETAIL_CATEGORY_CONTENT
                SET STATUS = %s
                WHERE BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (status, biz_detail_category_content_id))
            connection.commit()
            
            # rowcount를 통해 업데이트 성공 여부 확인
            if cursor.rowcount == 0:
                return False  # 업데이트된 행이 없는 경우 False 반환
            return True  # 업데이트 성공 시 True 반환
    except pymysql.MySQLError as e:
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")
    finally:
        if cursor:
            close_cursor(cursor)
        close_connection(connection)



# 글 상세 조회
def select_category_for_detail_content(biz_detail_category_content_id: int):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 첫 번째 쿼리: 제목, 내용 정보 조회
            select_content_query = """
                SELECT 
                    BIZ_DETAIL_CATEGORY_CONTENT_ID,
                    TITLE,
                    CONTENT,
                    STATUS
                FROM
                    BIZ_DETAIL_CATEGORY_CONTENT
                WHERE
                    BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """
            cursor.execute(select_content_query, (biz_detail_category_content_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="해당하는 매장 정보를 찾을 수 없습니다."
                )

            # 두 번째 쿼리: 이미지 정보 조회
            select_images_query = """
                SELECT 
                    BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL
                FROM
                    BIZ_DETAIL_CATEGORY_CONTENT_IMAGE  
                WHERE
                    BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """

            cursor.execute(select_images_query, (biz_detail_category_content_id,))
            images = cursor.fetchall()
            image_urls = [CategoryImage(biz_detail_category_content_image_url=image["BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL"]) for image in images]

            # 결과를 Pydantic 모델 형식에 맞춰 반환
            result = CategoryDetailContentResponse(
                category_detail_content=CategoryDetailContent(
                    biz_detail_category_content_id=row["BIZ_DETAIL_CATEGORY_CONTENT_ID"],
                    title=row["TITLE"],
                    content=row["CONTENT"],
                    status=row["STATUS"]
                ),
                image=image_urls
            )
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred CategoryDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")



# 게시글 삭제
def delete_category_content_status(biz_detail_category_content_id: int) -> bool:
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            delete_query = """
                UPDATE BIZ_DETAIL_CATEGORY_CONTENT
                SET STATUS = 'D'
                WHERE BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(delete_query, (biz_detail_category_content_id))
            connection.commit()
            
            # rowcount를 통해 업데이트 성공 여부 확인
            if cursor.rowcount == 0:
                return False  # 업데이트된 행이 없는 경우 False 반환
            return True  # 업데이트 성공 시 True 반환
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()


# 게시글 수정
def update_category_content(biz_detail_category_content_id: int, title: str, content: str) -> bool:
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE 
                    BIZ_DETAIL_CATEGORY_CONTENT
                SET 
                    TITLE = %s,
                    CONTENT = %s
                WHERE BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (title, content, biz_detail_category_content_id))
            connection.commit()

            # rowcount를 통해 업데이트 성공 여부 확인
            return cursor.rowcount > 0  # 업데이트된 행이 없으면 False 반환
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()

def select_category_existing_image(biz_detail_category_content_id : int):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            select_query = """
                SELECT 
                    BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL
                FROM BIZ_DETAIL_CATEGORY_CONTENT_IMAGE
                WHERE BIZ_DETAIL_CATEGORY_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(select_query, (biz_detail_category_content_id))
            rows = cursor.fetchall()
            if not rows:
                return []

            result = [
                CategoryImage(
                    biz_detail_category_content_image_url=row["BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL"],
                )
                for row in rows
            ]
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()

# 기존 이미지 삭제
def delete_category_existing_image(biz_detail_category_content_id: int, images_to_delete: List[str]):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 기존 이미지 목록에서 삭제할 이미지 조건을 추가
            delete_query = """
                DELETE FROM BIZ_DETAIL_CATEGORY_CONTENT_IMAGE
                WHERE BIZ_DETAIL_CATEGORY_CONTENT_ID = %s AND BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL IN (%s)
            """
            # 이미지 URL 리스트를 쿼리에 맞게 변환
            formatted_urls = ', '.join(['%s'] * len(images_to_delete))
            final_query = delete_query % (biz_detail_category_content_id, formatted_urls)

            # 쿼리 실행
            cursor.execute(final_query, images_to_delete)
            connection.commit()

            # 삭제된 행의 개수 확인
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="해당하는 매장 이미지 정보를 찾을 수 없습니다.",
                )

            return True

    except pymysql.MySQLError as e:
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")
    finally:
        connection.close()




def insert_category_new_image(biz_detail_category_content_id: int, new_image_urls: List[str]):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 데이터 인서트 쿼리
            insert_query = """
                INSERT INTO BIZ_DETAIL_CATEGORY_CONTENT_IMAGE
                (BIZ_DETAIL_CATEGORY_CONTENT_ID, BIZ_DETAIL_CATEGORY_CONTENT_IMAGE_URL) 
                VALUES (%s, %s)
            """
            # URL 리스트를 각 튜플로 구성
            data_to_insert = [(biz_detail_category_content_id, url) for url in new_image_urls]
            
            # 여러 개의 레코드 삽입
            cursor.executemany(insert_query, data_to_insert)

            # 커밋하여 DB에 반영
            connection.commit()
    except pymysql.MySQLError as e:
        connection.rollback()  # 오류 시 롤백
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")

    finally:
        close_connection(connection)  # 연결 종료
