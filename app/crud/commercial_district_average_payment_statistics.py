import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.statistics import CommercialStatistics


def select_commercial_district_average_payment_info(
    city_id: int, district_id: int, sub_district_id: int, detail_category_id: int
):
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
                    FROM COMMERCIAL_DISTRICT_AVERAGE_PAYMENT_STATISTICS
                    WHERE CITY_ID = %s AND DISTRICT_ID = %s AND SUB_DISTRICT_ID=%s AND BIZ_DETAIL_CATEGORY_ID = %s
                    ;
                """
                cursor.execute(
                    select_query,
                    (city_id, district_id, sub_district_id, detail_category_id),
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
        print(f"Error selecting from average_payment: {e}")
        raise
