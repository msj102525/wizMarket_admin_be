from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.ads import AdsList, AdsInitInfo
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


# 기본 정보 가져오기
def select_ads_init_info(store_business_number: str) -> AdsInitInfo:
    connection = get_re_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    try:
        if connection.open:
            select_query = """
                SELECT 
                    STORE_BUSINESS_NUMBER, 
                    STORE_NAME,
                    ROAD_NAME,
                    CITY_NAME,
                    DISTRICT_NAME,
                    SUB_DISTRICT_NAME,
                    LATITUDE,
                    LONGITUDE,
                    DETAIL_CATEGORY_NAME,
                    LOC_INFO_AVERAGE_SALES_K,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_MON,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_TUE,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_WED,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_THU,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_FRI,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SAT,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SUN, 
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_06_09,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_09_12,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_12_15,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_15_18,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_18_21,
                    COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_21_24,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_20S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_30S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_40S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_50S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_60_OVER,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_20S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_30S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_40S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_50S,
                    COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_60_OVER
                FROM
                    REPORT
                WHERE
                    STORE_BUSINESS_NUMBER = %s
                ;
            """
            cursor.execute(select_query, (store_business_number,))
            row = cursor.fetchone()  # 한 행만 가져옴

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"AdsInitInfo {store_business_number}에 해당하는 데이터를 찾을 수 없습니다.",
                )

            # Pydantic 모델로 매핑
            ads_init_info = AdsInitInfo(
                store_business_number=row.get("STORE_BUSINESS_NUMBER"),
                store_name=row.get("STORE_NAME"),
                road_name=row.get("ROAD_NAME"),
                city_name=row.get("CITY_NAME"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                latitude= row.get("LATITUDE"),
                longitude=row.get("LONGITUDE"),
                detail_category_name=row.get("DETAIL_CATEGORY_NAME"),
                loc_info_average_sales_k=row.get("LOC_INFO_AVERAGE_SALES_K"),
                commercial_district_average_percent_mon = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_MON"),
                commercial_district_average_percent_tue = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_TUE"),
                commercial_district_average_percent_wed = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_WED"),
                commercial_district_average_percent_thu = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_THU"),
                commercial_district_average_percent_fri = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_FRi"),
                commercial_district_average_percent_sat = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SAT"),
                commercial_district_average_percent_sun = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SUN"),
                commercial_district_average_percent_06_09 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_06_09"),
                commercial_district_average_percent_09_12 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_09_12"),
                commercial_district_average_percent_12_15 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_12_15"),
                commercial_district_average_percent_15_18 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_15_18"),
                commercial_district_average_percent_18_21 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_18_21"),
                commercial_district_average_percent_21_24 = row.get("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_21_24"),
                commercial_district_avg_client_per_m_20s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_20S"),
                commercial_district_avg_client_per_m_30s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_30S"),
                commercial_district_avg_client_per_m_40s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_40S"),
                commercial_district_avg_client_per_m_50s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_50S"),
                commercial_district_avg_client_per_m_60_over = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_60_OVER"),
                commercial_district_avg_client_per_f_20s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_20S"),
                commercial_district_avg_client_per_f_30s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_30S"),
                commercial_district_avg_client_per_f_40s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_40S"),
                commercial_district_avg_client_per_f_50s = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_50S"),
                commercial_district_avg_client_per_f_60_over = row.get("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_60_OVER"),
            )
            return ads_init_info
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"Unexpected Error in select_ads_init_info: {e}")
        raise HTTPException(status_code=500, detail="알 수 없는 오류가 발생했습니다.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

