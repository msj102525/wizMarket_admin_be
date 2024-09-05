import pymysql
from app.db.connect import get_db_connection, close_connection
from typing import Optional

def fetch_loc_info_by_ids(city_id: int, district_id: int, sub_district_id: int) -> Optional[dict]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT * FROM loc_info
            WHERE city_id = %s AND district_id = %s AND sub_district_id = %s
        """
        cursor.execute(query, (city_id, district_id, sub_district_id))
        result = cursor.fetchone()
        return result
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_filtered_locations(filters):
    """주어진 필터 조건을 바탕으로 데이터를 조회하는 함수"""

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = "SELECT * FROM loc_info WHERE 1=1"
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if "city" in filters:
            query += " AND city_id = %s"
            query_params.append(filters["city"])

        if "district" in filters:
            query += " AND district_id = %s"
            query_params.append(filters["district"])

        if "sub_district" in filters:
            query += " AND sub_district_id = %s"
            query_params.append(filters["sub_district"])

        if filters.get("move_popMin") is not None:
            query += " AND move_pop >= %s"
            query_params.append(filters["move_popMin"])

        if filters.get("move_popMax") is not None:
            query += " AND move_pop <= %s"
            query_params.append(filters["move_popMax"])

        if filters.get("houseMin") is not None:
            query += " AND house >= %s"
            query_params.append(filters["houseMin"])

        if filters.get("houseMax") is not None:
            query += " AND house <= %s"
            query_params.append(filters["houseMax"])


        # 실행될 쿼리 출력 (디버깅용)
        query_with_params = query % tuple(query_params)
        print("실행할 쿼리:", query_with_params)  # 쿼리 출력

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료