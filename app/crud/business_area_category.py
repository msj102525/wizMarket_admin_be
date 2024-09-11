import pymysql
from app.db.connect import get_db_connection, close_connection
from typing import Optional

def get_business_area_category_from_db(reference_id: int):
    connection = get_db_connection()
    cursor = None

    try:
        with connection.cursor() as cursor:
            # reference_id를 기반으로 데이터를 조회하는 쿼리
            sql = "SELECT * FROM business_area_category WHERE reference_id = %s"
            cursor.execute(sql, (reference_id,))
            result = cursor.fetchall()  # 결과 가져오기
            return result
    finally:
        connection.close()  # 연결 닫기