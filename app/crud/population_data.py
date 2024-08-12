import pymysql
from app.db.connect import get_db_connection
import mysql.connector  # 예외 처리를 위해 필요

async def get_population_data(srchFrYm: str, srchToYm: str, region: str, subRegion: str):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT * FROM population_data 
            WHERE ctpvNm = %s AND sggNm LIKE %s AND statsYm BETWEEN %s AND %s
            """
            cursor.execute(sql, (region, f"%{subRegion}%", srchFrYm, srchToYm))
            result = cursor.fetchall()
        return result
    finally:
        connection.close()

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
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # Duplicate entry error code
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
        connection.close()
