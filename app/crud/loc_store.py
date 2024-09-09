import pymysql
from app.db.connect import get_db_connection
# crud/loc_store.py


def get_filtered_store(filters, page, limit, sort_by, order):
    """주어진 필터 조건을 바탕으로 데이터를 조회하는 함수"""
    
    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()  # DB 연결 함수
    cursor = None

    try:
        # 기본 쿼리 생성
        query = """
            SELECT temp.loc_store_id, temp.store_name, temp.branch_name, temp.road_name_address, 
                   temp.large_category_name, temp.medium_category_name, temp.small_category_name, temp.industry_name,
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

        # 필터 조건이 있을 경우 쿼리에 추가
        if "store_name" in filters and filters["store_name"]:
            query += " AND temp.store_name ILIKE %s"
            query_params.append(f"%{filters['store_name']}%")  # 부분 검색을 위해 LIKE 사용

        if "city" in filters and filters["city"]:
            query += " AND temp.city_id = %s"
            query_params.append(filters["city"])

        if "district" in filters and filters["district"]:
            query += " AND temp.district_id = %s"
            query_params.append(filters["district"])

        if "sub_district" in filters and filters["sub_district"]:
            query += " AND temp.sub_district_id = %s"
            query_params.append(filters["sub_district"])
        
        if "selectedQuarter" in filters and filters["selectedQuarter"]:
            query += " AND temp.Y_Q = %s"
            query_params.append(filters["selectedQuarter"])

        # 정렬 조건이 있을 경우 추가 (기본값: store_name 오름차순)
        sort_by = filters.get("sort_by", "store_name")
        order = filters.get("order", "asc").lower()
        if order not in ["asc", "desc"]:
            order = "asc"  # 기본값으로 설정

        query += f" ORDER BY {sort_by} {order.upper()}"

        # 페이징 처리 (limit와 offset)
        page = filters.get("page", 1)
        limit = filters.get("limit", 20)
        offset = (page - 1) * limit

        query += " LIMIT %s OFFSET %s"
        query_params.extend([limit, offset])

        # 쿼리 실행
        cursor = connection.cursor()
        cursor.execute(query, query_params)
        
        # 결과 가져오기
        results = cursor.fetchall()

        return results

    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
        return []

    finally:
        if cursor:
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
