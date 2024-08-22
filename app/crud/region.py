import pymysql
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def get_region_id(city: str, district: str, sub_district: str):
    connection = get_db_connection()
    cursor = None
    try:
        if connection.open:
            cursor = connection.cursor()
            sql = """
                SELECT REGION_ID FROM REGION 
                WHERE CITY = %s AND DISTRICT = %s AND SUB_DISTRICT = %s
            """
            cursor.execute(sql, (city, district, sub_district))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                return None

    except pymysql.MySQLError as e:
        print(f"Database query failed: {e}")
        rollback(connection)

    finally:
        close_cursor(cursor)
        close_connection(connection)
