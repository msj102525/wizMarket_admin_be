from typing import List
import pymysql
from pymysql import MySQLError
from app.schemas.commercial_district import (
    CommercialDistrictCreate,
    CommercialDistrictOutput,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)

input_data = {
    "location": {
        "city": "서울특별시",
        "district": "강남구",
        "sub_district": "개포1동",
    },
    "category": {
        "main": "음식",
        "sub": "간이주점",
        "detail": "호프/맥주",
    },
    "density": {
        "national": "1.7%",
        "city": "2.3%",
        "district": "1.8%",
        "sub_district": "1.1%",
    },
    "market_size": "104,745만원",
    "average_sales": "4,345만원",
    "average_payment_cost": "71,372원",
    "usage_count": "12,175건",
    "average_profit": {
        "sales": "4,345만원",
        "operating_cost": "1,100만원",
        "food": "200만원",
        "employee": "300만원",
        "rental": "150만원",
        "tax": "100만원",
        "family_employee": "50만원",
        "ceo": "100만원",
        "etc": "200만원",
        "amount": "1,004만원",
        "percent": "23.1%",
    },
    "sales_by_day": {
        "most_profitable_day": "Saturday",
        "percent": "19.6%",
        "details": {
            "Monday": "10.6%",
            "Tuesday": "13.7%",
            "Wednesday": "13.1%",
            "Thursday": "16.9%",
            "Friday": "13.8%",
            "Saturday": "19.6%",
            "Sunday": "12.4%",
        },
    },
    "sales_by_time": {
        "most_profitable_time": "21_24",
        "percent": "56.0%",
        "details": {
            "06_09": "0.0%",
            "09_12": "2.2%",
            "12_15": "3.7%",
            "15_18": "2.9%",
            "18_21": "18.8%",
            "21_24": "56.0%",
            "24_06": "16.4%",
        },
    },
    "client_demographics": {
        "dominant_gender": "남성",
        "dominant_gender_percent": 68.7,
        "dominant_age_group": "40대",
        "age_groups": ["20대", "30대", "40대", "50대", "60대"],
        "male_percents": [3.2, 14.3, 20.8, 21.2, 9.2],
        "female_percents": [1.5, 6.3, 10.2, 8.7, 4.5],
        "total_male_percent": 67.1,
        "total_female_percent": 32.8,
        "most_visitor_age": "60대이상 여성 1위",
    },
    "top5_menus": {
        "top5_menu_1": "국산생맥주",
        "top5_menu_2": "소주",
        "top5_menu_3": "국산병맥주",
        "top5_menu_4": "건어물구이",
        "top5_menu_5": "수입병맥주",
    },
}


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
            market_size, average_sales, average_payment_cost, usage_count, #4
            average_profit_amount, average_profit_percent, average_operating_cost, #3
            average_food, average_employee, average_rental, average_tax, average_family_employee, #5
            average_ceo, average_etc, #2
            most_profitable_day, day_percent, sales_monday, sales_tuesday, sales_wednesday, #5
            sales_thursday, sales_friday, sales_saturday, sales_sunday, #4
            most_profitable_time, time_percent, sales_06_09, sales_09_12, sales_12_15, #5
            sales_15_18, sales_18_21, sales_21_24, sales_24_06, #4
            dominant_gender, dominant_gender_percent, dominant_age_group, #3
            most_visitor_age, male_20s, male_30s, male_40s, male_50s, male_60s, #6
            female_20s, female_30s, female_40s, female_50s, female_60s, #5
            total_male_percent, total_female_percent, #2
            top_menu_1, top_menu_2, top_menu_3, top_menu_4, top_menu_5 #5
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s,
                %s, %s, %s, %s, 
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s
            );
            """

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
                data["average_payment_cost"],
                data["usage_count"],
                data["average_profit"]["amount"],
                data["average_profit"]["percent"],
                data["average_profit"]["operating_cost"],
                data["average_profit"]["food"],
                data["average_profit"]["employee"],
                data["average_profit"]["rental"],
                data["average_profit"]["tax"],
                data["average_profit"]["family_employee"],
                data["average_profit"]["ceo"],
                data["average_profit"]["etc"],
                data["sales_by_day"]["most_profitable_day"],
                data["sales_by_day"]["percent"],
                data["sales_by_day"]["details"].get("Monday", None),
                data["sales_by_day"]["details"].get("Tuesday", None),
                data["sales_by_day"]["details"].get("Wednesday", None),
                data["sales_by_day"]["details"].get("Thursday", None),
                data["sales_by_day"]["details"].get("Friday", None),
                data["sales_by_day"]["details"].get("Saturday", None),
                data["sales_by_day"]["details"].get("Sunday", None),
                data["sales_by_time"]["most_profitable_time"],
                data["sales_by_time"]["percent"],
                data["sales_by_time"]["details"].get("06_09", None),
                data["sales_by_time"]["details"].get("09_12", None),
                data["sales_by_time"]["details"].get("12_15", None),
                data["sales_by_time"]["details"].get("15_18", None),
                data["sales_by_time"]["details"].get("18_21", None),
                data["sales_by_time"]["details"].get("21_24", None),
                data["sales_by_time"]["details"].get("24_06", None),
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
                data["client_demographics"]["total_male_percent"],
                data["client_demographics"]["total_female_percent"],
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


def select_all_commercial_district_by_sub_district(
    sub_district: str,
) -> List[CommercialDistrictOutput]:
    connection = get_db_connection()
    cursor = None
    results = []
    try:
        if connection.open:
            cursor = connection.cursor()
            select_query = """
                SELECT *
                FROM COMMERCIAL_DISTRICT
                WHERE SUB_DISTRICT LIKE %s;
            """
            cursor.execute(select_query, (sub_district,))
            rows = cursor.fetchall()

            for row in rows:
                try:
                    results.append(
                        CommercialDistrictOutput(
                            id=row[0],
                            city=row[1],
                            district=row[2],
                            sub_district=row[3],
                            main_category=row[4],
                            sub_category=row[5],
                            detail_category=row[6],
                            national_density=row[7],
                            city_density=row[8],
                            district_density=row[9],
                            sub_district_density=row[10],
                            market_size=row[11],
                            average_sales=row[12],
                            average_operating_cost=row[14],
                            average_food=row[15],
                            average_employee=row[16],
                            average_rental=row[17],
                            average_tax=row[18],
                            average_family_employee=row[19],
                            average_ceo=row[20],
                            average_etc=row[25],
                            average_payment_cost=row[21],
                            usage_count=row[22],
                            average_profit_amount=row[23],
                            average_profit_percent=row[24],
                            most_profitable_day=row[26],
                            day_percent=row[26],
                            sales_monday=row[27],
                            sales_tuesday=row[28],
                            sales_wednesday=row[29],
                            sales_thursday=row[30],
                            sales_friday=row[31],
                            sales_saturday=row[32],
                            sales_sunday=row[33],
                            time_percent=row[34],
                            most_profitable_time=row[35],
                            sales_06_09=row[37],
                            sales_09_12=row[38],
                            sales_12_15=row[39],
                            sales_15_18=row[39],
                            sales_18_21=row[40],
                            sales_21_24=row[41],
                            sales_24_06=row[42],
                            dominant_gender=row[43],
                            dominant_gender_percent=row[44],
                            dominant_age_group=row[45],
                            most_visitor_age=row[46],
                            male_20s=row[47],
                            male_30s=row[48],
                            male_40s=row[49],
                            male_50s=row[50],
                            male_60s=row[51],
                            female_20s=row[52],
                            female_30s=row[53],
                            female_40s=row[54],
                            female_50s=row[55],
                            female_60s=row[56],
                            total_male_percent=row[57],
                            total_female_percent=row[58],
                            top_menu_1=row[59],
                            top_menu_2=row[60],
                            top_menu_3=row[61],
                            top_menu_4=row[62],
                            top_menu_5=row[63],
                            created_at=row[64],
                            updated_at=row[65],
                        )
                    )
                    print(row)
                except Exception as e:
                    print(f"Error processing row {row}: {e}")
    except Exception as e:
        print(f"Database query failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.open:
            connection.close()
    return results


if __name__ == "__main__":
    # print(input_data["sales_by_time"]["details"].get("12_15", None))
    # print(input_data["sales_by_time"]["details"].get("15_18", None))
    insert_commercial_district(input_data)
