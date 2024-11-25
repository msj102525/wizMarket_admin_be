from datetime import date
import logging
from typing import List, Optional

from fastapi import HTTPException
import pymysql
from app.schemas.rising_business import (
    RisingBusinessDataDate,
    RisingBusinessOutput,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)

logger = logging.getLogger(__name__)


def select_all_rising_business_by_dynamic_query(
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    sub_district_id: Optional[int] = None,
    biz_main_category_id: Optional[int] = None,
    biz_sub_category_id: Optional[int] = None,
    biz_detail_category_id: Optional[int] = None,
    growth_rate_min: Optional[float] = None,
    growth_rate_max: Optional[float] = None,
    rank_min: Optional[int] = None,
    rank_max: Optional[int] = None,
    y_m: Optional[date] = None,
) -> List[RisingBusinessOutput]:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)
    results: List[RisingBusinessOutput] = []

    try:
        if connection.open:
            params = [
                city_id,
                district_id,
                sub_district_id,
                biz_main_category_id,
                biz_sub_category_id,
                biz_detail_category_id,
                growth_rate_min,
                growth_rate_max,
                rank_min,
                rank_max,
                y_m,
            ]
            select_query = """
            WITH FilteredRB as (
                SELECT *
                FROM RISING_BUSINESS RB
                WHERE 1=1
                    AND RB.CITY_ID = COALESCE(%s, RB.CITY_ID)
                    AND RB.DISTRICT_ID = COALESCE(%s, RB.DISTRICT_ID)
                    AND RB.SUB_DISTRICT_ID = COALESCE(%s, RB.SUB_DISTRICT_ID)
                    AND RB.BIZ_MAIN_CATEGORY_ID = COALESCE(%s, RB.BIZ_MAIN_CATEGORY_ID)
                    AND RB.BIZ_SUB_CATEGORY_ID = COALESCE(%s, RB.BIZ_SUB_CATEGORY_ID)
                    AND RB.BIZ_DETAIL_CATEGORY_ID = COALESCE(%s, RB.BIZ_DETAIL_CATEGORY_ID)
                    AND RB.GROWTH_RATE BETWEEN COALESCE(%s, RB.GROWTH_RATE) AND COALESCE(%s, RB.GROWTH_RATE)
                    AND RB.SUB_DISTRICT_RANK BETWEEN COALESCE(%s, RB.SUB_DISTRICT_RANK) AND COALESCE(%s, RB.SUB_DISTRICT_RANK)
                    AND RB.Y_M = COALESCE(%s, RB.Y_M)
            )
            SELECT
                RB.*,
                CI.CITY_NAME,
                DI.DISTRICT_NAME,
                SD.SUB_DISTRICT_NAME,
                BMC.BIZ_MAIN_CATEGORY_NAME,
                BSC.BIZ_SUB_CATEGORY_NAME,
                BDC.BIZ_DETAIL_CATEGORY_NAME
            FROM
                FilteredRB RB
            JOIN
                CITY CI ON RB.CITY_ID = CI.CITY_ID
            JOIN
                DISTRICT DI ON RB.DISTRICT_ID = DI.DISTRICT_ID
            JOIN
                SUB_DISTRICT SD ON RB.SUB_DISTRICT_ID = SD.SUB_DISTRICT_ID
            JOIN
                BIZ_MAIN_CATEGORY BMC ON RB.BIZ_MAIN_CATEGORY_ID = BMC.BIZ_MAIN_CATEGORY_ID
            JOIN
                BIZ_SUB_CATEGORY BSC ON RB.BIZ_SUB_CATEGORY_ID = BSC.BIZ_SUB_CATEGORY_ID
            JOIN
                BIZ_DETAIL_CATEGORY BDC ON RB.BIZ_DETAIL_CATEGORY_ID = BDC.BIZ_DETAIL_CATEGORY_ID
            AND BDC.BIZ_DETAIL_CATEGORY_NAME != '소분류없음'
            ORDER BY RB.RISING_BUSINESS_ID DESC
        """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, params)

            rows = cursor.fetchall()

            for row in rows:
                rising_business_ouput = RisingBusinessOutput(
                    rising_business_id=row.get("RISING_BUSINESS_ID"),
                    city_name=row.get("CITY_NAME"),
                    district_name=row.get("DISTRICT_NAME"),
                    sub_district_name=row.get("SUB_DISTRICT_NAME"),
                    biz_main_category_name=row.get("BIZ_MAIN_CATEGORY_NAME"),
                    biz_sub_category_name=row.get("BIZ_SUB_CATEGORY_NAME"),
                    biz_detail_category_name=row.get("BIZ_DETAIL_CATEGORY_NAME"),
                    growth_rate=(
                        row.get("GROWTH_RATE")
                        if row.get("GROWTH_RATE") is not None
                        else 0.0
                    ),
                    sub_district_rank=(
                        row.get("SUB_DISTRICT_RANK")
                        if row.get("SUB_DISTRICT_RANK") is not None
                        else 0
                    ),
                    y_m=row.get("Y_M"),
                    created_at=row.get("CREATED_AT"),
                    updated_at=row.get("UPDATED_AT"),
                )
                results.append(rising_business_ouput)

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
        rollback(connection)
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        rollback(connection)
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


def select_rising_business_data_date() -> List[RisingBusinessDataDate]:

    try:
        with get_db_connection() as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_query = """
                    SELECT
                        Y_M
                    FROM
                        RISING_BUSINESS
                    GROUP BY Y_M
                    ;
                """

                cursor.execute(select_query)
                rows = cursor.fetchall()

                # logger.info(f"rows: {rows}")

                results = []

                for row in rows:
                    result = RisingBusinessDataDate(y_m=row["Y_M"])

                    results.append(result)

                return results

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error occurred in select_rising_business_data_date: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
