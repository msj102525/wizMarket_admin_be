import logging
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def get_or_create_biz_detail_category_id(
    biz_sub_category_id: int, biz_detail_category_name: str
) -> int:
    connection = get_db_connection()
    cursor = connection.cursor()
    logger = logging.getLogger(__name__)

    try:
        select_query = """
        SELECT biz_detail_category_id
        FROM biz_detail_category
        WHERE biz_sub_category_id = %s
        AND biz_detail_category_name = %s;
        """
        cursor.execute(
            select_query,
            (biz_sub_category_id, biz_detail_category_name),
        )
        result = cursor.fetchone()

        logger.info(
            "Executing query: %s with parameters: (%s, %s)",
            select_query,
            biz_sub_category_id,
            biz_detail_category_name,
        )

        if result:
            return result[0]
        else:
            insert_query = """
            INSERT INTO biz_detail_category
            (biz_sub_category_id, biz_detail_category_name)
            VALUES (%s, %s);
            """
            cursor.execute(
                insert_query,
                (biz_sub_category_id, biz_detail_category_name),
            )
            commit(connection)

            return cursor.lastrowid
    except Exception as e:
        rollback(connection)
        logger.error(
            "Error in get_or_create_biz_detail_category_id: %s", e, exc_info=True
        )
    finally:
        close_cursor(cursor)
        close_connection(connection)


def get_detail_category_name_by_detial_category_id(detail_category_id: int) -> str:
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        select_query = "SELECT biz_detail_category_name FROM biz_detail_category WHERE biz_detail_category_id = %s;"
        cursor.execute(select_query, (detail_category_id,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return ""
    except Exception as e:
        rollback(connection)
        print(f"get_detail_category_name:{e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)


# if __name__ == "__main__":
#     print(get_or_create_biz_detail_category_id(1, "호프/맥주"))
