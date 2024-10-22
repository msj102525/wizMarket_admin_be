import logging
from fastapi import logger
import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.statistics import CommercialStatistics


def select_commercial_district_sub_district_density_info(
    city_id: int, district_id: int, sub_district_id: int, detail_category_id: int
):
    # print(detail_category_id)
    # DB 연결
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)
    results = []

    try:
        # stat_item 테이블에서 데이터 조회하는 SQL 쿼리 작성
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
            ;
        """
        cursor.execute(
            select_query, (city_id, district_id, sub_district_id, detail_category_id)
        )
        row = cursor.fetchone()

        # logger.info(
        #     f"Generated SQL Query: {select_query, (city_id,district_id, sub_district_id, detail_category_id )}"
        # )

        # print(row)

        # if row is None:
        #     print("No data found for the given parameters")
        #     return (
        #         CommercialStatistics()
        #     )  # 기본값으로 초기화된 CommercialStatistics 반환

        # 결과 생성 (row.get()으로 기본값 처리)
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
        print(f"Error selecting from sub_district_density: {e}")
        connection.rollback()  # Rollback if there's an error
        raise  # Re-raise the exception after rollback

    finally:
        close_cursor(cursor)
        close_connection(connection)
