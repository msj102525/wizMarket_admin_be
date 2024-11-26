from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.ads import AdsList, AdsInitInfo, AdsImageList
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError


load_dotenv()
logger = logging.getLogger(__name__)


def select_ads_list():
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    a.ADS_ID,
                    a.STORE_BUSINESS_NUMBER,
                    r.STORE_NAME,
                    r.ROAD_NAME,
                    a.USE_OPTION,
                    a.TITLE,
                    a.DETAIL_TITLE,
                    a.CONTENT,
                    a.STATUS,
                    a.CREATED_AT
                FROM
                    ADS a
                STRAIGHT_JOIN REPORT r
                ON r.STORE_BUSINESS_NUMBER = a.STORE_BUSINESS_NUMBER
                AND a.STATUS != 'D';

            """
            cursor.execute(select_query)
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="AdsList 해당하는 매장 정보를 찾을 수 없습니다.",
                )
            result = [
                AdsList(
                    ads_id=row["ADS_ID"],
                    store_business_number=row["STORE_BUSINESS_NUMBER"],
                    store_name=row["STORE_NAME"],
                    road_name=row["ROAD_NAME"],
                    use_option=row["USE_OPTION"],
                    title=row["TITLE"],
                    detail_title=row["DETAIL_TITLE"],
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
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기


# 이미지 미리보기 처리를 위한 이미지 리스트 가져오기
def select_ads_image_list(ads_id: int):
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    ADS_IMAGE_ID,
                    ADS_ID,
                    ADS_IMAGE_URL
                FROM
                    ADS_IMAGE
                WHERE
                    ADS_ID = %s
            """
            cursor.execute(select_query, (ads_id,))  # ads_id를 쿼리에 바인딩
            rows = cursor.fetchall()
            result = [
                AdsImageList(
                    ads_image_id=row["ADS_IMAGE_ID"],
                    ads_id=row["ADS_ID"],
                    ads_image_url=row["ADS_IMAGE_URL"],
                )
                for row in rows
            ]
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred in select_ads_image_list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기



# 게시 상태 여부 업데이트
def update_ads_status(ads_id: int, status: str) -> bool:
    connection = get_re_db_connection()
    try:
        with connection.cursor() as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE ADS
                SET STATUS = %s
                WHERE ADS_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (status, ads_id))
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


# 필터 조회
def select_filters_list(filters):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    a.ADS_ID,
                    a.STORE_BUSINESS_NUMBER,
                    r.STORE_NAME,
                    r.ROAD_NAME,
                    a.USE_OPTION,
                    a.TITLE,
                    a.DETAIL_TITLE,
                    a.CONTENT,
                    a.STATUS,
                    a.CREATED_AT
                FROM
                    ADS a
                STRAIGHT_JOIN REPORT r
                ON r.STORE_BUSINESS_NUMBER = a.STORE_BUSINESS_NUMBER
                WHERE a.STATUS != 'D'
            """

            query_params = []

            # 필터 조건 추가
            if filters.get("use_option"):
                select_query += " AND a.USE_OPTION = %s"
                query_params.append(filters["use_option"])

            if filters.get("title"):
                select_query += " AND a.TITLE = %s"
                query_params.append(filters["title"])

            if filters.get("match_type") == "=" and filters.get("store_name"):
                select_query += " AND r.STORE_NAME = %s"
                query_params.append(filters["store_name"])

            if filters.get("match_type") == "LIKE" and filters.get("store_name"):
                select_query += " AND r.STORE_NAME LIKE %s"
                query_params.append(f"%{filters['store_name']}%")

            # 커서 실행
            cursor.execute(select_query, query_params)
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="AdsList 해당하는 매장 정보를 찾을 수 없습니다.",
                )
            result = [
                AdsList(
                    ads_id=row["ADS_ID"],
                    store_business_number=row["STORE_BUSINESS_NUMBER"],
                    store_name=row["STORE_NAME"],
                    road_name=row["ROAD_NAME"],
                    use_option=row["USE_OPTION"],
                    title=row["TITLE"],
                    detail_title=row["DETAIL_TITLE"],
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
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기


