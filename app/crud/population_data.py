import pymysql
from app.db.connect import get_db_connection, close_connection

async def get_population_data(srchFrYm: str, srchToYm: str, region: str, subRegion: str):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT * FROM populationdata 
            WHERE ctpvNm LIKE %s AND sggNm LIKE %s AND statsYm BETWEEN %s AND %s
            """
            cursor.execute(sql, (f"%{region}%", f"%{subRegion}%", srchFrYm, srchToYm))
            result = cursor.fetchall()
        return result
    finally:
        close_connection(connection)

def insert_record(table_name: str, **kwargs):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['%s'] * len(kwargs))
            values = tuple(kwargs.values())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        connection.commit()
    except pymysql.IntegrityError as e:
        if e.args[0] == 1062:  # Duplicate entry error code
            print(f"Duplicate entry found for {kwargs}. Skipping...")
        else:
            print(f"Error inserting data: {e}")
            connection.rollback()
            raise e
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
        raise e
    finally:
        close_connection(connection)
