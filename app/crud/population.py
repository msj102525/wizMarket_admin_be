import pymysql
import pandas as pd
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback
from app.schemas.population import Population
from typing import List
from mysql.connector.cursor import MySQLCursorDict
from typing import List, Dict
import decimal


def check_previous_month_data_exists(connection, previous_month):
    """저번 달 데이터가 DB에 존재하는지 확인하는 함수."""
    
    query = """
        SELECT COUNT(*) AS count
        FROM population
        WHERE reference_date = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (previous_month,))
        result = cursor.fetchone()
    
    # COUNT 값을 반환
    return result[0] > 0

def convert_decimal_to_float(data):
    if isinstance(data, list):
        for item in data:
            for key, value in item.items():
                if isinstance(value, decimal.Decimal):
                    item[key] = float(value)
    return data



def get_filtered_population_data(filters):
    # 데이터베이스 연결
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()

        # 기본 쿼리
        query = """
            SELECT 
                p.POPULATION_ID AS pop_id,                
                city.city_name AS city_name,              
                district.district_name AS district_name,   
                sub_district.sub_district_name AS subdistrict_name,  
                ROUND((p.male_population / p.total_population) * 100, 2) AS male_percentage,  
                ROUND((p.female_population / p.total_population) * 100, 2) AS female_percentage, 

                
                (p.age_0 + p.age_1 + p.age_2 + p.age_3 + p.age_4 + p.age_5 + p.age_6 + p.age_7 + p.age_8 + p.age_9) AS under_10,
                (p.age_10 + p.age_11 + p.age_12 + p.age_13 + p.age_14 + p.age_15 + p.age_16 + p.age_17 + p.age_18 + p.age_19) AS age_10s,
                (p.age_20 + p.age_21 + p.age_22 + p.age_23 + p.age_24 + p.age_25 + p.age_26 + p.age_27 + p.age_28 + p.age_29) AS age_20s,
                (p.age_30 + p.age_31 + p.age_32 + p.age_33 + p.age_34 + p.age_35 + p.age_36 + p.age_37 + p.age_38 + p.age_39) AS age_30s,
                (p.age_40 + p.age_41 + p.age_42 + p.age_43 + p.age_44 + p.age_45 + p.age_46 + p.age_47 + p.age_48 + p.age_49) AS age_40s,
                (p.age_50 + p.age_51 + p.age_52 + p.age_53 + p.age_54 + p.age_55 + p.age_56 + p.age_57 + p.age_58 + p.age_59) AS age_50s,
                (p.age_60 + p.age_61 + p.age_62 + p.age_63 + p.age_64 + p.age_65 + p.age_66 + p.age_67 + p.age_68 + p.age_69 +
                p.age_70 + p.age_71 + p.age_72 + p.age_73 + p.age_74 + p.age_75 + p.age_76 + p.age_77 + p.age_78 + p.age_79 +
                p.age_80 + p.age_81 + p.age_82 + p.age_83 + p.age_84 + p.age_85 + p.age_86 + p.age_87 + p.age_88 + p.age_89 +
                p.age_90 + p.age_91 + p.age_92 + p.age_93 + p.age_94 + p.age_95 + p.age_96 + p.age_97 + p.age_98 + p.age_99 + 
                p.age_100 + p.age_101 + p.age_102 + p.age_103 + p.age_104 + p.age_105 + p.age_106 + p.age_107 + p.age_108 + 
                p.age_109 + p.age_110_over) AS age_60_plus,
                p.reference_date

            FROM population p
            JOIN city ON p.CITY_ID = city.city_id               
            JOIN district ON p.DISTRICT_ID = district.district_id 
            JOIN sub_district ON p.SUB_DISTRICT_ID = sub_district.sub_district_id
            WHERE 1 = 1

        """

        # 필터 조건에 따라 쿼리 구성
        params = []

        # 시/도 필터
        if 'city' in filters:
            query += " AND p.city_id = %s"
            params.append(filters['city'])

        # 군/구 필터
        if 'district' in filters:
            query += " AND p.district_id = %s"
            params.append(filters['district'])

        # 읍/면/동 필터
        if 'subDistrict' in filters:
            query += " AND p.sub_district_id = %s"
            params.append(filters['subDistrict'])


        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        result = cursor.fetchall()
        result = convert_decimal_to_float(result)  # Decimal 값을 float으로 변환

        print(type(result))
        print(result[0])

        for key, value in result[0].items():
            print(f"Key: {key}, Value: {value}, Type: {type(value)}")

        return result

    finally:
        # 커서와 연결 닫기
        if cursor:
            cursor.close()
        if connection:
            connection.close()





def insert_population_data(connection, population_data: Population):
    with connection.cursor() as cursor:
        insert_query = """
        INSERT INTO population (
            CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID, GENDER_ID, admin_code, reference_date,
            province_name, district_name, subdistrict_name, total_population, male_population, female_population,
            age_0, age_1, age_2, age_3, age_4, age_5, age_6, age_7, age_8, age_9,
            age_10, age_11, age_12, age_13, age_14, age_15, age_16, age_17, age_18, age_19,
            age_20, age_21, age_22, age_23, age_24, age_25, age_26, age_27, age_28, age_29,
            age_30, age_31, age_32, age_33, age_34, age_35, age_36, age_37, age_38, age_39,
            age_40, age_41, age_42, age_43, age_44, age_45, age_46, age_47, age_48, age_49,
            age_50, age_51, age_52, age_53, age_54, age_55, age_56, age_57, age_58, age_59,
            age_60, age_61, age_62, age_63, age_64, age_65, age_66, age_67, age_68, age_69,
            age_70, age_71, age_72, age_73, age_74, age_75, age_76, age_77, age_78, age_79,
            age_80, age_81, age_82, age_83, age_84, age_85, age_86, age_87, age_88, age_89,
            age_90, age_91, age_92, age_93, age_94, age_95, age_96, age_97, age_98, age_99,
            age_100, age_101, age_102, age_103, age_104, age_105, age_106, age_107, age_108, age_109,
            age_110_over, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, NOW(), NOW()
        )
        """

        population_data_tuple = (
        population_data.city_id,
        population_data.district_id,
        population_data.sub_district_id,
        population_data.gender_id,
        population_data.admin_code,
        population_data.reference_date,
        population_data.province_name,
        population_data.district_name,
        population_data.subdistrict_name,
        population_data.total_population,
        population_data.male_population,
        population_data.female_population,
        population_data.age_0, population_data.age_1, population_data.age_2, population_data.age_3,
        population_data.age_4, population_data.age_5, population_data.age_6, population_data.age_7,
        population_data.age_8, population_data.age_9, population_data.age_10, population_data.age_11,
        population_data.age_12, population_data.age_13, population_data.age_14, population_data.age_15,
        population_data.age_16, population_data.age_17, population_data.age_18, population_data.age_19,
        population_data.age_20, population_data.age_21, population_data.age_22, population_data.age_23,
        population_data.age_24, population_data.age_25, population_data.age_26, population_data.age_27,
        population_data.age_28, population_data.age_29, population_data.age_30, population_data.age_31,
        population_data.age_32, population_data.age_33, population_data.age_34, population_data.age_35,
        population_data.age_36, population_data.age_37, population_data.age_38, population_data.age_39,
        population_data.age_40, population_data.age_41, population_data.age_42, population_data.age_43,
        population_data.age_44, population_data.age_45, population_data.age_46, population_data.age_47,
        population_data.age_48, population_data.age_49, population_data.age_50, population_data.age_51,
        population_data.age_52, population_data.age_53, population_data.age_54, population_data.age_55,
        population_data.age_56, population_data.age_57, population_data.age_58, population_data.age_59,
        population_data.age_60, population_data.age_61, population_data.age_62, population_data.age_63,
        population_data.age_64, population_data.age_65, population_data.age_66, population_data.age_67,
        population_data.age_68, population_data.age_69, population_data.age_70, population_data.age_71,
        population_data.age_72, population_data.age_73, population_data.age_74, population_data.age_75,
        population_data.age_76, population_data.age_77, population_data.age_78, population_data.age_79,
        population_data.age_80, population_data.age_81, population_data.age_82, population_data.age_83,
        population_data.age_84, population_data.age_85, population_data.age_86, population_data.age_87,
        population_data.age_88, population_data.age_89, population_data.age_90, population_data.age_91,
        population_data.age_92, population_data.age_93, population_data.age_94, population_data.age_95,
        population_data.age_96, population_data.age_97, population_data.age_98, population_data.age_99,
        population_data.age_100, population_data.age_101, population_data.age_102, population_data.age_103,
        population_data.age_104, population_data.age_105, population_data.age_106, population_data.age_107,
        population_data.age_108, population_data.age_109, population_data.age_110_over
        )

        cursor.execute(insert_query, population_data_tuple)




    