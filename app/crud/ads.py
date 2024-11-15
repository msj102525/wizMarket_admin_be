from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.ads import AdsList
from typing import Optional, List


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
                    a.TITLE,
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
                    local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                    store_business_number=row["STORE_BUSINESS_NUMBER"],
                    store_name=row["STORE_NAME"],
                    road_name=row["ROAD_NAME"],
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
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기


def select_ads_init_info():
    pass