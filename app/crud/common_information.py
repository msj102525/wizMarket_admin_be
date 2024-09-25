import logging
from typing import List
import pymysql
import pandas as pd
from app.schemas.city import City
from app.db.connect import (
    get_db_connection,
    get_report_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)
from app.schemas.common_information import CommonInformation


def get_all_report_common_information() -> List[CommonInformation]:
    connection = get_report_db_connection(True)
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    results: List[CommonInformation] = []

    try:
        select_query = """
            SELECT *
            FROM
            t_common_information
            ORDER BY common_information_id DESC;
        """
        cursor.execute(select_query)

        rows = cursor.fetchall()

        for row in rows:
            common_information = CommonInformation(
                common_information_id=row["common_information_id"],
                title=row["title"],
                content=row["content"],
                file_group_id=row["file_group_id"],
                is_deleted=row["is_deleted"],
                etc=row["etc"],
                reg_id=row["reg_id"],
                reg_date=row["reg_date"],
                mod_id=row["mod_id"],
                mod_date=row["mod_date"],
            )
            results.append(common_information)

        return results

    except Exception as e:
        connection.rollback()
        logging.error("Error fetching common information: %s", e)
        raise e
    finally:
        close_cursor(cursor)
        close_connection(connection)
