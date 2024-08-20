import pymysql
from pymysql import MySQLError
from app.schemas.commercial_district import CommercialDistrictCreate
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)

# input_data = {
#     "location": {"city": "서울특별시", "district": "강남구", "sub_district": "개포1동"},
#     "category": {"main": "음식", "sub": "간이주점", "detail": "호프/맥주"},
#     "density": {
#         "national": "1.7%",
#         "city": "2.3%",
#         "district": "1.8%",
#         "sub_district": "1.1%",
#     },
#     "market_size": "104,745만원",
#     "average_sales": "4,345만원",
#     "average_price": "71,372원",
#     "usage_count": "12,175건",
#     "average_profit": {"amount": "1,004", "percent": "23.1%"},
#     "sales_by_day": {
#         "most_profitable_day": "Saturday",
#         "percent": "19.6%",
#         "details": {
#             "Monday": "10.6%",
#             "Tuesday": "13.7%",
#             "Wednesday": "13.1%",
#             "Thursday": "16.9%",
#             "Friday": "13.8%",
#             "Saturday": "19.6%",
#             "Sunday": "12.4%",
#         },
#     },
#     "sales_by_time": {
#         "most_profitable_time": "21_24",
#         "percent": "56.0%",
#         "details": {
#             "06_09": "0.0%",
#             "09_12": "2.2%",
#             "12_15": "3.7%",
#             "15_18": "2.9%",
#             "18_21": "18.8%",
#             "21_24": "56.0%",
#             "24_06": "16.4%",
#         },
#     },
#     "client_demographics": {
#         "dominant_gender": "남성",
#         "dominant_gender_percent": 68.7,
#         "dominant_age_group": "40대",
#         "age_groups": ["20대", "30대", "40대", "50대", "60대"],
#         "male_percents": [3.2, 14.3, 20.8, 21.2, 9.2],
#         "female_percents": [1.5, 6.3, 10.2, 8.7, 4.5],
#         "most_visitor_age": "60대이상 여성 1위",
#     },
#     "top5_menus": {
#         "top5_menu_1": "국산생맥주",
#         "top5_menu_2": "소주",
#         "top5_menu_3": "국산병맥주",
#         "top5_menu_4": "건어물구이",
#         "top5_menu_5": "수입병맥주",
#     },
# }


def insert_commercial_district(data: CommercialDistrictCreate):
    connection = get_db_connection()
    cursor = None
    try:
        if connection.open:
            cursor = connection.cursor()

            # SQL 쿼리
            insert_query = """
            INSERT INTO COMMERCIAL_DISTRICT (
                city, district, sub_district, main_category, sub_category, detail_category, #6
                national_density, city_density, district_density, sub_district_density, #4
                market_size, average_sales, average_price, usage_count, #4
                average_profit_amount, average_profit_percent, #2
                most_profitable_day, day_percent, sales_monday, sales_tuesday, sales_wednesday, #5
                sales_thursday, sales_friday, sales_saturday, sales_sunday, #4
                most_profitable_time, time_percent, sales_06_09, sales_09_12, sales_12_15, #5
                sales_15_18, sales_18_21, sales_21_24, sales_24_06, #4
                dominant_gender, dominant_gender_percent, dominant_age_group, #3
                most_visitor_age, male_20s, male_30s, male_40s, male_50s, male_60s, #6
                female_20s, female_30s, female_40s, female_50s, female_60s, #5
                top_menu_1, top_menu_2, top_menu_3, top_menu_4, top_menu_5 #5
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s,
                %s, %s, %s, %s, 
                %s, %s, 
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            );
            """

            # 값 매핑
            values = (
                data["location"]["city"],
                data["location"]["district"],
                data["location"]["sub_district"],
                data["category"]["main"],
                data["category"]["sub"],
                data["category"]["detail"],
                data["density"]["national"],
                data["density"]["city"],
                data["density"]["district"],
                data["density"]["sub_district"],
                data["market_size"],
                data["average_sales"],
                data["average_price"],
                data["usage_count"],
                data["average_profit"]["amount"],
                data["average_profit"]["percent"],
                data["sales_by_day"]["most_profitable_day"],
                data["sales_by_day"]["percent"],
                data["sales_by_day"]["details"]["Monday"],
                data["sales_by_day"]["details"]["Tuesday"],
                data["sales_by_day"]["details"]["Wednesday"],
                data["sales_by_day"]["details"]["Thursday"],
                data["sales_by_day"]["details"]["Friday"],
                data["sales_by_day"]["details"]["Saturday"],
                data["sales_by_day"]["details"]["Sunday"],
                data["sales_by_time"]["most_profitable_time"],
                data["sales_by_time"]["percent"],
                data["sales_by_time"]["details"]["06_09"],
                data["sales_by_time"]["details"]["09_12"],
                data["sales_by_time"]["details"]["12_15"],
                data["sales_by_time"]["details"]["15_18"],
                data["sales_by_time"]["details"]["18_21"],
                data["sales_by_time"]["details"]["21_24"],
                data["sales_by_time"]["details"]["24_06"],
                data["client_demographics"]["dominant_gender"],
                data["client_demographics"]["dominant_gender_percent"],
                data["client_demographics"]["dominant_age_group"],
                data["client_demographics"]["most_visitor_age"],
                data["client_demographics"]["male_percents"][0],
                data["client_demographics"]["male_percents"][1],
                data["client_demographics"]["male_percents"][2],
                data["client_demographics"]["male_percents"][3],
                data["client_demographics"]["male_percents"][4],
                data["client_demographics"]["female_percents"][0],
                data["client_demographics"]["female_percents"][1],
                data["client_demographics"]["female_percents"][2],
                data["client_demographics"]["female_percents"][3],
                data["client_demographics"]["female_percents"][4],
                data["top5_menus"]["top5_menu_1"],
                data["top5_menus"]["top5_menu_2"],
                data["top5_menus"]["top5_menu_3"],
                data["top5_menus"]["top5_menu_4"],
                data["top5_menus"]["top5_menu_5"],
            )

            cursor.execute(insert_query, values)
            connection.commit()
            print(f"{data} : Data inserted successfully!")

    except MySQLError as e:
        print(f"MySQL Error: {e}")
        rollback(connection)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        rollback(connection)
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)


# if __name__ == "__main__":
#     insert_commercial_district(input_data)
