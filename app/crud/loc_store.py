import pymysql
from datetime import datetime

def insert_data_to_loc_store(connection, data):
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO loc_store (
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
                NOW(), NOW()
            )
            """

            # 디버깅을 위해 각 항목을 개별적으로 테스트
            try:
                print("Inserting CITY_ID:", data['CITY_ID'])
                print("Inserting DISTRICT_ID:", data['DISTRICT_ID'])
                print("Inserting SUB_DISTRICT_ID:", data['SUB_DISTRICT_ID'])
                print("Inserting StoreBusinessNumber:", data['StoreBusinessNumber'])
                # 필요한 모든 항목을 하나씩 출력
                # 생략된 나머지 항목들에 대해 동일하게 처리

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