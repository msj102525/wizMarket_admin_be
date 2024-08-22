import pymysql
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback
from app.schemas.population import Population


async def fetch_population_records(start_date: int, end_date: int, region_id: int):
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            sql = """
            SELECT * FROM population
            WHERE ID = %s AND `Y_M` BETWEEN %s AND %s
            """
            cursor.execute(sql, (region_id, start_date, end_date))
            records = cursor.fetchall()

            return records
    except pymysql.MySQLError as e:
        print(f"Error during record fetching: {e}")
        raise
    finally:
        close_cursor(cursor)
        close_connection(connection)


async def fetch_population_by_year_month(year_month: int):
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * FROM population WHERE `Y_M` = %s"
            cursor.execute(sql, (year_month,))
            records = cursor.fetchall()
            return records
    except pymysql.MySQLError as e:
        print(f"Error during record fetching: {e}")
        raise
    finally:
        close_cursor(cursor)
        close_connection(connection)


async def insert_population_to_db(df):
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
            cursor = connection.cursor()

            for _, row in df.iterrows():
                # 각 행 데이터를 데이터베이스에 삽입
                sql = """
                INSERT INTO population (REGION_ID, Y_M, TOTAL, MALETOTAL, FEMALETOTAL, ...)
                VALUES (%s, %s, %s, %s, %s, ...)
                """
                cursor.execute(sql, (
                    row['REGION_ID'],
                    row['Y_M'],
                    row['TOTAL'],
                    row['MALETOTAL'],
                    row['FEMALETOTAL'],
                    # 필요한 모든 컬럼 값을 추가
                ))
        
            commit(connection)

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        rollback(connection)
        raise

    finally:
        close_cursor(cursor)
        close_connection(connection)