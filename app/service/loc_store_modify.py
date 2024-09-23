import pymysql
from app.db.connect import get_db_connection, close_connection
from tqdm import tqdm

# district_id 가져오는 함수
def fetch_districts_by_city_id(city_id: int):
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT district_id, district_name FROM district WHERE city_id = %s"
        cursor.execute(query, (city_id,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error fetching districts for city_id {city_id}: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_loc_store_in_batches():
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        
        # city_id와 Y_Q 조건 설정
        city_ids = range(2, 18)  # city_id가 2~17인 경우
        y_q_values = ['2022%', '2023%', '2024%']  # Y_Q가 2022~2024인 경우

        batch_size = 500

        # tqdm 적용: 도시별 진행 상황을 표시
        for city_id in tqdm(city_ids, desc="Cities Progress", unit="city"):
            # 해당 city_id에 속한 district 가져오기
            districts = fetch_districts_by_city_id(city_id)
            
            for district in districts:
                district_id = district['district_id']
                print(f"Processing city_id {city_id}, district_id {district_id}")

                for y_q_value in y_q_values:
                    print(f"    Processing Y_Q {y_q_value}")

                    last_loc_store_id = 0  # 초기 PK 값

                    while True:
                        # 업데이트 쿼리 실행 (AUTO_INCREMENT 필드 기준으로 500개씩 처리)
                        update_query = """
                            UPDATE loc_store
                            SET info_year = LEFT(Y_Q, 4),
                                info_quarter = SUBSTRING_INDEX(SUBSTRING_INDEX(Y_Q, '.', -1), '/', 1)
                            WHERE city_id = %s
                              AND district_id = %s
                              AND Y_Q LIKE %s
                              AND loc_store_id > %s
                            ORDER BY loc_store_id
                            LIMIT %s
                        """
                        cursor.execute(update_query, (city_id, district_id, y_q_value, last_loc_store_id, batch_size))
                        
                        # 업데이트된 행의 수 확인
                        updated_rows = cursor.rowcount
                        if updated_rows == 0:
                            break
                        
                        # 마지막으로 처리된 loc_store_id 값 갱신
                        last_loc_store_id = cursor.lastrowid

        # 변경사항을 DB에 커밋
        connection.commit()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 함수 실행
if __name__ == "__main__":
    update_loc_store_in_batches()
