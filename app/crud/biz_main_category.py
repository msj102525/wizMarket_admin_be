import logging
import pandas as pd
from app.schemas.city import City
from dotenv import load_dotenv
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def get_or_create_biz_main_category_id(biz_main_category_name: str) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    # logger = logging.getLogger(__name__)

    try:
        select_query = "SELECT biz_main_category_id FROM biz_main_category WHERE biz_main_category_name = %s;"
        cursor.execute(select_query, (biz_main_category_name,))
        result = cursor.fetchone()
        # logger.info(f"Executing query: {select_query % (biz_main_category_name)}")

        if result:
            return result[0]
        else:
            insert_query = (
                "INSERT INTO biz_main_category (biz_main_category_name) VALUES (%s);"
            )
            cursor.execute(insert_query, (biz_main_category_name))
            commit(connection)

            return cursor.lastrowid
    except Exception as e:
        rollback(connection)
        print(f"get_or_create_biz_main_category_id:{e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)


def get_main_category_name_by_main_category_id(main_category_id: int) -> str:
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        select_query = "SELECT biz_main_category_name FROM biz_main_category WHERE biz_main_category_id = %s;"
        cursor.execute(select_query, (main_category_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return ""
    except Exception as e:
        rollback(connection)
        print(f"get_main_category_name:{e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)


if __name__ == "__main__":
    print(get_or_create_biz_main_category_id("음식"))
