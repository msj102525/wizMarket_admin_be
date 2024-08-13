from pymysql import MySQLError
from app.schemas.rising_business import RisingBusinessCreate, Location, BusinessDetail
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def insert_rising_business(data: RisingBusinessCreate):
    print('insert 작동')
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
            cursor = connection.cursor()

            # 데이터 삽입 쿼리
            insert_query = """
            INSERT INTO RISING_BUSINESS (city, district, sub_district, business_name, growth_rate)
            VALUES (%s, %s, %s, %s, %s);
            """

            for key, business_detail in data.rising_top5.items():
                values = (
                    data.location.city,
                    data.location.district,
                    data.location.sub_district,
                    business_detail.business_name,
                    (
                        business_detail.growth_rate
                        if business_detail.growth_rate is not None
                        else 0.00
                    ),
                )
                cursor.execute(insert_query, values)

            commit(connection)
            print(
                f"Data inserted for {data.location.city}, {data.location.district}, {data.location.sub_district}"
            )

    except MySQLError as e:
        print(f"Error: {e}")
        rollback(connection)

    finally:
        if cursor:
            close_cursor(cursor)
        if connection and connection.open:
            close_connection(connection)
