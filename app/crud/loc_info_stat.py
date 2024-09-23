import pymysql
from app.db.connect import get_db_connection, close_connection
from typing import List, Dict, Tuple
import statistics

# 전체 city_id 조회 함수
def fetch_all_city_ids() -> List[Dict]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT city_id, city_name FROM city"  # 필요한 컬럼만 선택
        cursor.execute(query)
        result = cursor.fetchall()  # 모든 결과를 리스트로 반환
        return result
    except Exception as e:
        print(f"Error fetching city_ids: {e}")
        return []  # 예외 발생 시 빈 리스트 반환
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 특정 city_id에 속한 district_id 조회 함수
def fetch_districts_by_city_id(city_id: int) -> List[Dict]:
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
        return []  # 예외 발생 시 빈 리스트 반환
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# 통계 계산 함수
def calculate_statistics(city_id: int, district_id: int) -> Dict[str, float]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 특정 city와 district에 대한 통계 계산
        if city_id == 0:
            # 전국 통계 계산 (city_id = 0)
            query = "SELECT district_id, shop FROM loc_info"
            cursor.execute(query)
        elif district_id == 0:  # city 전체 통계 계산
            query = "SELECT district_id, shop FROM loc_info WHERE city_id = %s"
            cursor.execute(query, (city_id,))
        else:  # 특정 city와 district에 대한 통계 계산
            query = "SELECT district_id, shop FROM loc_info WHERE city_id = %s AND district_id = %s"
            cursor.execute(query, (city_id, district_id))
        
        result = cursor.fetchall()

        # 전체 shop 값을 기준으로 순위 계산을 위해 리스트로 변환
        shop_values = [row['shop'] for row in result]
        district_ids = [row['district_id'] for row in result]

        if not shop_values:
            return {
                "average": 0,
                "median": 0,
                "std_dev": 0,
                "max": 0,
                "min": 0,
                "ranking_score": 0
            }

        # 전체 데이터를 기준으로 평균, 중위수, 표준편차, 최대값, 최소값 계산
        average = statistics.mean(shop_values)
        median = statistics.median(shop_values)
        std_dev = statistics.stdev(shop_values) if len(shop_values) > 1 else 0
        max_value = max(shop_values)
        min_value = min(shop_values)

        # 전체 데이터에서 순위 계산
        sorted_shop_values = sorted(shop_values, reverse=True)
        ranking_scores = []
        total_count = len(shop_values)

        for idx, shop_value in enumerate(shop_values):
            # 해당 값의 순위를 계산
            rank = sorted_shop_values.index(shop_value) + 1
            # 0~10 점수화
            ranking_score = 10 * ((total_count + 1 - rank) / total_count)
            ranking_scores.append({
                "district_id": district_ids[idx],
                "ranking_score": ranking_score
            })

        # 전체 통계 및 개별 동별 점수 반환
        return {
            "average": average,
            "median": median,
            "std_dev": std_dev,
            "max": max_value,
            "min": min_value,
            "ranking_scores": ranking_scores  # 동별 점수 리스트로 반환
        }
    
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {}
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
