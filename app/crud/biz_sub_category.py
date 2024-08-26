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


def get_or_create_biz_sub_category_id(
    biz_main_category_id: int, biz_sub_category_name: str
) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    logger = logging.getLogger(__name__)

    try:
        select_query = """
        SELECT biz_sub_category_id FROM
        biz_sub_category WHERE biz_main_category_id = %s
        AND biz_sub_category_name = %s
        ;
        """
        cursor.execute(select_query, (biz_main_category_id, biz_sub_category_name))
        result = cursor.fetchone()

        logger.info(
            f"Executing query: {select_query % (biz_main_category_id, biz_sub_category_name)}"
        )

        if result:
            return result[0]
        else:
            insert_query = """
            INSERT INTO biz_sub_category
            (biz_main_category_id, biz_sub_category_name)
            VALUES (%s, %s)
            ;
            """

            cursor.execute(insert_query, (biz_main_category_id, biz_sub_category_name))
            commit(connection)

            return cursor.lastrowid
    except Exception as e:
        rollback(connection)
        print(f"get_or_create_biz_sub_category_id:{e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)


# if __name__ == "__main__":
#     print(get_or_create_biz_sub_category_id(1, "간이주점"))
