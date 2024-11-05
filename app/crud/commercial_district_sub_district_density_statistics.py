from datetime import date
import logging
from fastapi import logger
import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.statistics import CommercialStatistics


import logging


def select_commercial_district_sub_district_density_info(
    city_id: int,
    district_id: int,
    sub_district_id: int,
    detail_category_id: int,
    y_m: date,
):
    logger = logging.getLogger(__name__)

    try:
        with get_db_connection() as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_query = """
                    SELECT
                        AVG_VAL,
                        MED_VAL,
                        STD_VAL,
                        MAX_VAL,
                        MIN_VAL,
                        J_SCORE
                    FROM COMMERCIAL_DISTRICT_SUB_DISTRICT_DENSITY_STATISTICS
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
                    return CommercialStatistics()

                result = CommercialStatistics(
                    avg_val=row["AVG_VAL"],
                    med_val=row["MED_VAL"],
                    std_val=row["STD_VAL"],
                    max_val=row["MAX_VAL"],
                    min_val=row["MIN_VAL"],
                    j_score=row["J_SCORE"],
                )

                return result

    except Exception as e:
        logger.error(f"Error selecting from sub_district_density: {e}")
        raise
