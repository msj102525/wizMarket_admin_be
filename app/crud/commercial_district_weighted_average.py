from datetime import date
import logging
from fastapi import logger
import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.statistics import CommercialStatistics


import logging


def select_commercial_district_j_score_weighted_avg(
    city_id: int,
    district_id: int,
    sub_district_id: int,
    detail_category_id: int,
    y_m: date,
) -> float:
    logger = logging.getLogger(__name__)

    try:
        with get_db_connection() as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_query = """
                    SELECT
                        J_SCORE_AVG
                    FROM COMMERCIAL_DISTRICT_WEIGHTED_AVERAGE
                    WHERE CITY_ID = %s AND DISTRICT_ID = %s AND SUB_DISTRICT_ID=%s AND BIZ_DETAIL_CATEGORY_ID = %s
                    AND REF_DATE = %s
                    ;
                """
                cursor.execute(
                    select_query,
                    (city_id, district_id, sub_district_id, detail_category_id, y_m),
                )
                row = cursor.fetchone()

                if row is None:
                    return 0.0

                result = row["J_SCORE_AVG"]

                return result

    except Exception as e:
        logger.error(f"Error select_commercial_district_j_score_weighted_avg: {e}")
        raise
