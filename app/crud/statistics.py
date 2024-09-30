import pymysql
from app.db.connect import get_db_connection, close_connection, close_cursor
from app.schemas.statistics import StatisticsJscoreOutput


# stat_item id 조회
def select_state_item_id(table_name: str, column_name: str) -> int:

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT
                STAT_ITEM_ID
            FROM
                STAT_ITEM
            WHERE
                TABLE_NAME = %s
            AND
                COLUMN_NAME = %s
            ;
        """

        cursor.execute(select_query, (table_name, column_name))
        row = cursor.fetchone()

        return row["STAT_ITEM_ID"]

    finally:
        if cursor:
            cursor.close()
        connection.close()


############### 값 조회 ######################
def get_stat_data(filters_dict):
    print(filters_dict)

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   district.district_name AS district_name, 
                   sub_district.sub_district_name AS sub_district_name,
                   statistics.sub_district_id,
                   stat_item.column_name as column_name,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VALUE, MIN_VALUE, J_SCORE
            FROM statistics
            JOIN city ON statistics.city_id = city.city_id
            JOIN district ON statistics.district_id = district.district_id
            LEFT JOIN sub_district ON statistics.sub_district_id = sub_district.sub_district_id
            JOIN stat_item ON statistics.STAT_ITEM_ID = stat_item.STAT_ITEM_ID
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND statistics.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND statistics.district_id = %s"
            query_params.append(filters_dict["district"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        print(query)

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


########## 모든 city_id 값 가져오기 ###################
def get_all_city_ids():
    """
    모든 city_id를 가져오는 함수
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        query = """
            SELECT DISTINCT city_id
            FROM loc_info
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # city_id 목록을 반환
        return [row["city_id"] for row in result]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


############ 전국 단위 모든 city_id, district_id ##############
def get_all_city_district_pairs():
    """
    모든 city_id와 district_id 쌍을 가져옴
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 모든 city_id와 district_id 쌍을 가져오는 쿼리
        query = """
            SELECT DISTINCT city_id, district_id
            FROM loc_info
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # city_id, district_id 쌍을 반환
        return [(row["city_id"], row["district_id"]) for row in result]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


############ 전국 단위 모든 city_id, district_id, sub_district_id 값 ##############


def get_all_city_district_sub_district():
    """
    모든 city_id와 district_id, sub_district_id 쌍을 가져옴
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 모든 city_id와 district_id 쌍을 가져오는 쿼리
        query = """
            SELECT DISTINCT city_id, district_id, sub_district_id
            FROM loc_info
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # city_id, district_id 쌍을 반환
        return [
            (row["city_id"], row["district_id"], row["sub_district_id"])
            for row in result
        ]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


def get_data_for_city_and_district(city_id, district_id):
    """
    특정 city_id와 district_id에 대한 매장 수(shop count)를 가져옴
    여러 sub_district의 매장 수를 합산하여 반환
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # city_id와 district_id에 해당하는 모든 sub_district_id의 매장 수를 가져오는 쿼리
        query = """
            SELECT SUM(RESIDENT) AS total_shop_count
            FROM loc_info
            WHERE city_id = %s AND district_id = %s
        """

        cursor.execute(query, (city_id, district_id))
        result = cursor.fetchone()

        # 매장 수가 존재하지 않으면 0으로 처리
        total_shop_count = (
            result["total_shop_count"] if result["total_shop_count"] is not None else 0
        )

        return total_shop_count

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


def get_national_data():
    """
    전국 단위 매장 데이터를 가져오는 함수
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 전국 단위 매장 데이터를 가져오는 쿼리
        query = """
            SELECT resident
            FROM loc_info
        """
        cursor.execute(query)
        result = cursor.fetchall()

        # shop 데이터만 리스트로 반환
        return [row[0] for row in result]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


def get_city_district_data(city_id, district_id):
    """
    특정 시/군/구의 매장 데이터를 가져오는 함수
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 특정 시/군/구의 매장 데이터를 가져오는 쿼리
        query = """
            SELECT resident
            FROM loc_info
            WHERE city_id = %s AND district_id = %s
        """
        cursor.execute(query, (city_id, district_id))
        result = cursor.fetchall()

        # shop 데이터만 리스트로 반환
        return [row[0] for row in result]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


def get_all_city_district_pairs():
    """
    모든 시/군/구의 city_id와 district_id 쌍을 가져오는 함수
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 모든 시/군/구의 city_id, district_id 쌍을 가져오는 쿼리
        query = """
            SELECT DISTINCT city_id, district_id
            FROM loc_info
        """
        cursor.execute(query)
        result = cursor.fetchall()

        # city_id, district_id 쌍을 리스트로 반환
        return [(row[0], row[1]) for row in result]

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


############## 읍면동 단위 모든 shop 정보 가져오기 ################
# 매장 수(shop)를 loc_info 테이블에서 가져오는 함수
def get_j_score_national_data(national_data):
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    j_score_data = []

    try:
        for city_id, district_id, sub_district_id in national_data:
            query = """
                SELECT resident
                FROM loc_info
                WHERE city_id = %s AND district_id = %s AND sub_district_id = %s
            """
            cursor.execute(query, (city_id, district_id, sub_district_id))
            result = cursor.fetchone()  # 해당 읍/면/동의 shop 데이터를 하나 가져옴

            if result:
                # 튜플 (city_id, district_id, sub_district_id, shop_count)를 리스트에 추가
                j_score_data.append(
                    (city_id, district_id, sub_district_id, result["resident"])
                )
            else:
                # 만약 데이터가 없는 경우 shop_count를 0으로 설정
                j_score_data.append((city_id, district_id, sub_district_id, 0))

    except Exception as e:
        print(f"Error fetching j_score national data: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)

    return j_score_data  # j_score 데이터를 반환


############ 전국 j_score 데이터 넣기 ##################


def insert_j_score_nation(data):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO statistics (STAT_ITEM_ID, city_id, district_id, sub_district_id, j_score, CREATED_AT, ref, ref_date, stat_level)
            VALUES (8, %s, %s, %s, %s, now(), 'sbiz', '2024-08-01', 전국)
        """
        cursor.executemany(query, data)
        connection.commit()

    except Exception as e:
        print(f"Error inserting data: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


########## 전국 통계 업데이트 ###############
def update_stat_nation(national_stats):
    connection = None
    cursor = None
    try:
        # DB 연결
        connection = get_db_connection()
        cursor = connection.cursor()

        # SQL 업데이트 쿼리
        update_query = """
        UPDATE statistics 
        SET 
            AVG_VAL = %s, 
            MED_VAL = %s, 
            STD_VAL = %s, 
            MAX_VALUE = %s, 
            MIN_VALUE = %s
        WHERE STAT_ITEM_ID = 8;
        """

        # 딕셔너리에서 통계 값 추출
        avg_val = national_stats.get("average")
        med_val = national_stats.get("median")
        std_val = national_stats.get("stddev")
        max_val = national_stats.get("max")
        min_val = national_stats.get("min")

        # 쿼리 실행
        cursor.execute(update_query, (avg_val, med_val, std_val, max_val, min_val))

        # 변경사항 커밋
        connection.commit()
        print("Statistics updated successfully.")

    except pymysql.MySQLError as e:
        print(f"Error updating statistics: {e}")
        connection.rollback()
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


############## 지역별 통계 인서트 ###################


def insert_stat_region(city_district_stats_list):
    connection = None
    cursor = None

    try:
        # 데이터베이스 연결
        connection = get_db_connection()
        cursor = connection.cursor()

        # INSERT 쿼리 작성 (sub_district_id와 j_score는 지금 없으므로 NULL 또는 적절히 처리)
        query = """
            INSERT INTO statistics (STAT_ITEM_ID, city_id, district_id, sub_district_id, AVG_VAL, MED_VAL, STD_VAL, MAX_VALUE, MIN_VALUE, stat_level, CREATED_AT, ref, ref_date)
            VALUES (8, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'sbiz', '2024-08-01')
        """

        # 데이터를 튜플 형식으로 변환 후 executemany로 여러 행을 한 번에 삽입
        data_to_insert = [
            (
                item["city_id"],
                item["district_id"],
                None,  # sub_district_id가 없으므로 None
                item["statistics"]["average"],
                item["statistics"]["median"],
                item["statistics"]["stddev"],
                item["statistics"]["max"],
                item["statistics"]["min"],
                "시군구",  # stat_level이 시군구 레벨이라는 가정
            )
            for item in city_district_stats_list
        ]

        # 여러 행을 한 번에 인서트
        cursor.executemany(query, data_to_insert)
        connection.commit()

        print(f"Successfully inserted {cursor.rowcount} rows into the statistics table")

    except Exception as e:
        print(f"Error inserting data: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


########### 지역별 j_score 업데이트 ###############
def update_j_score_data_region(j_score_data_region):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            UPDATE statistics
            SET j_score = %s
            WHERE city_id = %s
            AND district_id = %s
            AND sub_district_id is null
            AND stat_item_id = 8
        """

        # 각 튜플에 대해 업데이트 쿼리를 실행
        for data in j_score_data_region:
            city_id, district_id, _, j_score = data  # j_score가 마지막에 위치
            cursor.execute(query, (j_score, city_id, district_id))

        connection.commit()
        print("J-score updated successfully.")

    except Exception as e:
        print(f"Error updating j_score: {e}")
        if connection:
            connection.rollback()

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


# 전국 jscore 조회
def select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
    stat_item_id: int, sub_district_id: int
) -> StatisticsJscoreOutput:

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                J_SCORE
            FROM
                statistics
            WHERE STAT_ITEM_ID = %s
            AND
                SUB_DISTRICT_ID = %s;
        """

        cursor.execute(select_query, (stat_item_id, sub_district_id))
        row = cursor.fetchone()

        return row["J_SCORE"]

    finally:
        if cursor:
            cursor.close()
        connection.close()
