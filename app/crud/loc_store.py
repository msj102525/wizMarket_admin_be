import pymysql
from app.db.connect import get_db_connection
# crud/loc_store.py

def parse_quarter(quarter_str):
    year, quarter = quarter_str.split(".")
    return int(year), int(quarter)



def get_filtered_loc_store(filters: dict):

    connection = get_db_connection()
    cursor = None
    total_items = 0  # 총 아이템 개수를 저장할 변수

    try:
        # 총 개수 구하기 위한 쿼리
        count_query = """
            SELECT COUNT(*) as total
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE 1=1 and local_year = 2024 and local_quarter = 2
        """
        query_params = []

        # 필터 조건 추가 (총 개수 구하는 쿼리에도 동일한 조건 사용)
        if filters.get("city") is not None:
            count_query += " AND local_store.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district") is not None:
            count_query += " AND local_store.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict") is not None:
            count_query += " AND local_store.sub_district_id = %s"
            query_params.append(filters["subDistrict"])
        
        if filters.get("mainCategory") is not None:
            count_query += " AND local_store.large_category_code = %s"
            query_params.append(filters["mainCategory"])
        
        
        if filters.get("subCategory") is not None:
            count_query += " AND local_store.medium_category_code = %s"
            query_params.append(filters["subCategory"])
        
        if filters.get("detailCategory") is not None:
            count_query += " AND local_store.small_category_code = %s"
            query_params.append(filters["detailCategory"])
        

        # 백엔드에서 검색 쿼리 처리
        if filters.get('storeName'):
            if filters.get('matchType') == '=':
                count_query += " AND local_store.store_name = %s"
                query_params.append(filters['storeName'])  # 정확히 일치
            else:
                count_query += " AND local_store.store_name LIKE %s"
                query_params.append(f"{filters['storeName']}%")  # '바%'로 시작하는 상호 검색


        # 총 개수 계산 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(count_query, query_params)
        total_items = cursor.fetchone()["total"]  # 총 개수

        # 데이터를 가져오는 쿼리 (페이징 적용)
        data_query = """
            SELECT 
                local_store.local_store_id, local_store.store_name, local_store.branch_name, local_store.road_name_address,
                local_store.large_category_name, local_store.medium_category_name, local_store.small_category_name,
                local_store.industry_name, local_store.building_name, local_store.new_postal_code, local_store.dong_info, local_store.floor_info,
                local_store.unit_info, local_store.local_year, local_store.local_quarter, local_store.CREATED_AT, local_store.UPDATED_AT,
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """
        
        # 동일한 필터 조건 적용
        data_query += count_query[count_query.find('WHERE 1=1') + len('WHERE 1=1'):]  # 필터 조건 재사용
        data_query += " ORDER BY local_store.store_name"

        # 페이징 처리
        page = filters.get("page", 1)  # 기본값 1
        page_size = filters.get("page_size", 20)  # 기본값 20
        offset = (page - 1) * page_size

        # LIMIT과 OFFSET 추가
        data_query += " LIMIT %s OFFSET %s"
        query_params.append(page_size)
        query_params.append(offset)

        print(data_query)
        # 데이터 조회 쿼리 실행
        cursor.execute(data_query, query_params)
        result = cursor.fetchall()

        return result, total_items  # 데이터와 총 개수 반환

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료






def check_previous_quarter_data_exists(connection, year, quarter):
    """저번 분기의 데이터가 DB에 있는지 확인하는 함수"""
    
    # SQL 쿼리 작성 (저번 분기의 데이터가 존재하는지 확인)
    query = "SELECT COUNT(*) AS count FROM local_store WHERE local_year = %s AND local_quarter = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(query, (year, quarter))
        result = cursor.fetchone()

    # count 값이 0이면 데이터가 없는 것
    return result[0] > 0




def insert_data_to_loc_store(connection, data):
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO local_store (
                CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID,  
                STORE_BUSINESS_NUMBER, store_name, branch_name,
                large_category_code, large_category_name,
                medium_category_code, medium_category_name,
                small_category_code, small_category_name,
                industry_code, industry_name,
                province_code, province_name, district_code,
                district_name, administrative_dong_code, administrative_dong_name,
                legal_dong_code, legal_dong_name,
                lot_number_code, land_category_code, land_category_name,
                lot_main_number, lot_sub_number, lot_address,
                road_name_code, road_name, building_main_number,
                building_sub_number, building_management_number, building_name,
                road_name_address, old_postal_code, new_postal_code,
                dong_info, floor_info, unit_info,
                longitude, latitude, local_year, local_quarter,
                CREATED_AT, UPDATED_AT
            ) VALUES (
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, %s,
                NOW(), NOW()
            )
            """

            # 디버깅을 위해 각 항목을 개별적으로 테스트
            try:
                cursor.execute(sql, (
                    data['CITY_ID'],
                    data['DISTRICT_ID'],
                    data['SUB_DISTRICT_ID'],
                    data['STORE_BUSINESS_NUMBER'],
                    data['store_name'],
                    data['branch_name'],
                    data['large_category_code'],
                    data['large_category_name'],
                    data['medium_category_code'],
                    data['medium_category_name'],
                    data['small_category_code'],
                    data['small_category_name'],
                    data['industry_code'],
                    data['industry_name'],
                    data['province_code'],
                    data['province_name'],
                    data['district_code'],
                    data['district_name'],
                    data['administrative_dong_code'],
                    data['administrative_dong_name'],
                    data['legal_dong_code'],
                    data['legal_dong_name'],
                    data['lot_number_code'],
                    data['land_category_code'],
                    data['land_category_name'],
                    data['lot_main_number'],
                    data['lot_sub_number'],
                    data['lot_address'],
                    data['road_name_code'],
                    data['road_name'],
                    data['building_main_number'],
                    data['building_sub_number'],
                    data['building_management_number'],
                    data['building_name'],
                    data['road_name_address'],
                    data['old_postal_code'],
                    data['new_postal_code'],
                    data['dong_info'],
                    data['floor_info'],
                    data['unit_info'],
                    data['longitude'],
                    data['latitude'],
                    data['local_year'],
                    data['local_quarter']
                ))

                connection.commit()

            except Exception as e:
                print(f"Error inserting specific data: {e}")
                raise

    except pymysql.MySQLError as e:
        print(f"Error inserting data into local_store: {e}")
        connection.rollback()
        raise
