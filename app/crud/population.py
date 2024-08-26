import pymysql
import pandas as pd
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback
from app.schemas.population import Population
from app.crud.city import get_or_create_region_id


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


async def insert_population_to_db(row, index):
    connection = None
    cursor = None

    try:
        # DB 연결
        connection = get_db_connection()
        cursor = connection.cursor()

        # 시도명, 시군구명, 읍면동명 값 가져오기
        city = row['시도명']
        district = row['시군구명'].split()[0]
        sub_district = row['읍면동명']

        # '출장소'라는 단어가 sub_district에 포함된 경우, 패스 처리
        if "출장소" in sub_district:
            print(f"Skipping row due to '출장소' in sub_district: {sub_district}")
            return  # 이 행을 건너뜀

        # 매핑 딕셔너리 생성 (변경 전 값을 키로, 변경 후 값을 값으로)
        sub_district_mapping = {
            "도화2.3동": "도화2,3동",
            "숭의1.3동": "숭의1,3동",
            "용현1.4동": "용현1,4동",
            "홍제제1동": "홍제1동",
            "홍제제2동": "홍제2동",
            "홍제제3동": "홍제3동",
            "봉명2송정동": "봉명2.송정동",
            "성화개신죽심동": "성화.개신.죽림동",
            "용담명암산성동": "용담.명암.산성동",
            "운천신봉동": "운천.신봉동",
            "율량사천동": "율량.사천동",
        }

        # 매핑 딕셔너리를 이용해 값 변경
        if sub_district in sub_district_mapping:
            sub_district = sub_district_mapping[sub_district]

        # region_id 조회 또는 생성
        region_id = get_or_create_region_id(city, district, sub_district)

        # 성별에 따라 컬럼 매핑
        if index % 2 == 0:
            # 짝수 인덱스 - 여성 데이터
            gender = 'F'
            to09 = row['to09F']
            to1019 = row['to1019F']
            to2029 = row['to2029F']
            to3039 = row['to3039F']
            to4049 = row['to4049F']
            to5059 = row['to5059F']
            to6069 = row['to6069F']
            to7079 = row['to7079F']
            to8089 = row['to8089F']
            to9099 = row['to9099F']
            over100 = row['over100F']
            total = row['계']
            maletotal = 0
            femaletotal = row['여자']
        else:
            # 홀수 인덱스 - 남성 데이터
            gender = 'M'
            to09 = row['to09M']
            to1019 = row['to1019M']
            to2029 = row['to2029M']
            to3039 = row['to3039M']
            to4049 = row['to4049M']
            to5059 = row['to5059M']
            to6069 = row['to6069M']
            to7079 = row['to7079M']
            to8089 = row['to8089M']
            to9099 = row['to9099M']
            over100 = row['over100M']
            total = row['계']
            maletotal = row['남자']
            femaletotal = 0

        # 연월 정보가 포함된 값 예시 (예: 202308)
        y_m = int(pd.to_datetime(row['기준연월']).strftime('%Y%m'))

        # population 테이블에 데이터 삽입
        insert_query = """
        INSERT INTO population 
        (ID, GENDER, TO09, TO1019, TO2029, TO3039, TO4049, TO5059, TO6069, TO7079, TO8089, TO9099, OVER100, TOTAL, MALETOTAL, FEMALETOTAL, Y_M) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            region_id, gender, to09, to1019, to2029, to3039, to4049, to5059, to6069, to7079, to8089, to9099, over100,
            total, maletotal, femaletotal, y_m
        ))

        # 변경 사항 커밋
        connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        if connection:
            connection.rollback()  # 문제가 발생하면 롤백

    finally:
        # 커서와 연결 종료
        if cursor:
            cursor.close()
        if connection:
            connection.close()