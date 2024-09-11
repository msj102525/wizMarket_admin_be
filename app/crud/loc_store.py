import pymysql
from app.db.connect import get_db_connection
# crud/loc_store.py


def get_filtered_loc_store(filters: dict):

    connection = get_db_connection()
    cursor = None

    try:
        query = """
                SELECT 
                    temp.loc_store_id, temp.store_name, temp.branch_name, temp.road_name_address,
                    temp.large_category_name, temp.medium_category_name, temp.small_category_name,
                    temp.industry_name, temp.building_name, temp.new_postal_code, temp.dong_info, temp.floor_info,
                    temp.unit_info, temp.Y_Q, temp.CREATED_AT, temp.UPDATED_AT,
                    city.city_name AS city_name, 
                    district.district_name AS district_name, 
                    sub_district.sub_district_name AS sub_district_name
                FROM temp
                JOIN city ON temp.city_id = city.city_id
                JOIN district ON temp.district_id = district.district_id
                JOIN sub_district ON temp.sub_district_id = sub_district.sub_district_id
                WHERE 1=1
            """
        query_params = []

        if filters.get("city") is not None:
            query += " AND temp.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district") is not None:
            query += " AND temp.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict") is not None:
            query += " AND temp.sub_district_id = %s"
            query_params.append(filters["subDistrict"])
        
        if filters.get("selectedQuarterMin") is not None:
            query += " AND temp.Y_Q >= %s"
            query_params.append(filters["selectedQuarterMin"])
        
        if filters.get("selectedQuarterMax") is not None:
            query += " AND temp.Y_Q <= %s"
            query_params.append(filters["selectedQuarterMax"])
        
        if filters.get("storeName") is not None:
            query += " AND temp.store_name LIKE %s"
            query_params.append(filters["storeName"])


        # 페이징 정보 처리
        page = filters.get("page", 1)  # 기본값 1
        page_size = filters.get("page_size", 20)  # 기본값 20
        offset = (page - 1) * page_size

        # 페이징을 위한 LIMIT과 OFFSET 추가
        query += " LIMIT %s OFFSET %s"
        query_params.append(page_size)  # LIMIT 값 (page_size)
        query_params.append(offset)  # OFFSET 값 (건너뛸 데이터 수)

        # 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()


        return result
    
    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료

    
# CRUD 레이어에서 필터 조건에 맞는 총 데이터 개수를 가져오는 함수
def get_total_item_count(filters: dict):
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용

    try:
        query = """
            SELECT 
                temp.loc_store_id, temp.store_name, temp.branch_name, temp.road_name_address,
                temp.large_category_name, temp.medium_category_name, temp.small_category_name,
                temp.industry_name, temp.building_name, temp.new_postal_code, temp.dong_info, temp.floor_info,
                temp.unit_info, temp.Y_Q, temp.CREATED_AT, temp.UPDATED_AT,
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name
            FROM temp
            JOIN city ON temp.city_id = city.city_id
            JOIN district ON temp.district_id = district.district_id
            JOIN sub_district ON temp.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """
        
        # 필터 적용 부분
        query_params = []

        if filters.get("city") is not None:
            query += " AND temp.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district") is not None:
            query += " AND temp.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict") is not None:
            query += " AND temp.sub_district_id = %s"
            query_params.append(filters["subDistrict"])
        
        if filters.get("selectedQuarterMin") is not None:
            query += " AND temp.Y_Q >= %s"
            query_params.append(filters["selectedQuarterMin"])
        
        if filters.get("selectedQuarterMax") is not None:
            query += " AND temp.Y_Q <= %s"
            query_params.append(filters["selectedQuarterMax"])
        
        if filters.get("storeName") is not None:
            query += " AND temp.store_name LIKE %s"
            query_params.append(filters["storeName"])


        # 총 데이터 개수 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        total_items = cursor.fetchall()

        print(type(total_items))

        return total_items

    finally:
        cursor.close()
        connection.close()





def check_previous_quarter_data_exists(connection, previous_quarter):
    """저번 분기의 데이터가 DB에 있는지 확인하는 함수"""
    
    # SQL 쿼리 작성 (저번 분기의 데이터가 존재하는지 확인)
    query = "SELECT COUNT(*) AS count FROM temp WHERE Y_Q = %s"
    
    with connection.cursor() as cursor:
        cursor.execute(query, (previous_quarter,))
        result = cursor.fetchone()

    # count 값이 0이면 데이터가 없는 것
    return result[0] > 0




def insert_data_to_loc_store(connection, data):
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO temp (
                CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID,  
                StoreBusinessNumber, store_name, branch_name,
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
                longitude, latitude, Y_Q,
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
                %s, %s, %s, 
                NOW(), NOW()
            )
            """

            # 디버깅을 위해 각 항목을 개별적으로 테스트
            try:
                cursor.execute(sql, (
                    data['CITY_ID'],
                    data['DISTRICT_ID'],
                    data['SUB_DISTRICT_ID'],
                    data['StoreBusinessNumber'],
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
                    data['Y_Q']
                ))

                connection.commit()

            except Exception as e:
                print(f"Error inserting specific data: {e}")
                raise

    except pymysql.MySQLError as e:
        print(f"Error inserting data into loc_store: {e}")
        connection.rollback()
        raise
