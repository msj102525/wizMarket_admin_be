import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.statistics import CommercialStatistics


def select_commercial_district_average_sales_info(
    city_id: int, district_id: int, sub_district_id: int, detail_category_id: int
):
    # print(detail_category_id)
    # DB 연결
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

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
            FROM COMMERCIAL_DISTRICT_AVERAGE_SALES_STATISTICS
            WHERE CITY_ID = %s AND DISTRICT_ID = %s AND SUB_DISTRICT_ID=%s AND BIZ_DETAIL_CATEGORY_ID = %s
            ;
        """
        cursor.execute(
            select_query, (city_id, district_id, sub_district_id, detail_category_id)
        )
        row = cursor.fetchone()

        # print(row)

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
        print(f"Error selecting from average_sales: {e}")
        connection.rollback()  # Rollback if there's an error
        raise  # Re-raise the exception after rollback

    finally:
        close_cursor(cursor)
        close_connection(connection)
