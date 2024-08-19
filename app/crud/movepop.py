import pymysql
from app.db.connect import get_db_connection, close_connection


async def get_population_data(srchFrYm: str, srchToYm: str, region: str):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT * FROM movepopdata 
            WHERE location LIKE %s AND yearmonth BETWEEN %s AND %s
            """
            cursor.execute(sql, (f"%{region}%", srchFrYm, srchToYm))
            result = cursor.fetchall()
        return result
    finally:
        close_connection(connection)