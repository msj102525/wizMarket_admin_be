import logging
from typing import List, Optional
from fastapi import HTTPException
import pymysql

from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)
from app.schemas.biz_detail_category import BizDetailCategoryOutput
from app.schemas.biz_main_category import BizMainCategoryOutput
from app.schemas.biz_sub_category import BizSubCategoryOutput
from app.schemas.category import CategoryListOutput


def get_all_sub_sub_detail_category_count() -> int:
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
            SELECT COUNT(CLASSIFICATION_ID) COUNT
            FROM CLASSIFICATION
            """
            cursor.execute(select_query)
            result = cursor.fetchone()

            return result["COUNT"]
    except Exception as e:
        print(f"get_all_detail_category_count Error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        close_connection(connection)


def get_all_classification_main_category(
    reference_id: int,
) -> List[BizMainCategoryOutput]:
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
            SELECT 
                MAIN_CATEGORY_CODE,
                MAIN_CATEGORY_NAME,
                COUNT(DISTINCT SUB_CATEGORY_CODE) AS SUB_CATEGORY_COUNT
            FROM 
                CLASSIFICATION 
            WHERE 
                REFERENCE_ID = %s
            GROUP BY 
                MAIN_CATEGORY_CODE, 
                MAIN_CATEGORY_NAME;
            """
            cursor.execute(select_query, (reference_id,))
            rows = cursor.fetchall()

            results: List[BizMainCategoryOutput] = []

            # Combine results
            for row in rows:
                biz_main_category_output = BizMainCategoryOutput(
                    biz_main_category_id=row.get("MAIN_CATEGORY_CODE"),
                    biz_main_category_name=row.get("MAIN_CATEGORY_NAME"),
                    biz_sub_category_count=row.get("SUB_CATEGORY_COUNT", 0),
                )
                results.append(biz_main_category_output)

            return results
    except Exception as e:
        print(f"get_all_classification_main_category Error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        close_connection(connection)


def get_all_classification_sub_category_by_main_category_code(
    main_category_code: str,
) -> List[BizSubCategoryOutput]:
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
            SELECT 
                SUB_CATEGORY_CODE, 
                SUB_CATEGORY_NAME, 
                COUNT(DISTINCT DETAIL_CATEGORY_CODE) AS DETAIL_CATEGORY_COUNT
            FROM 
                CLASSIFICATION 
            WHERE 
                MAIN_CATEGORY_CODE = %s 
            GROUP BY 
                SUB_CATEGORY_CODE, 
                SUB_CATEGORY_NAME;
            """
            cursor.execute(select_query, (main_category_code,))
            rows = cursor.fetchall()

            results: List[BizSubCategoryOutput] = []

            for row in rows:
                biz_sub_category_id = row.get("SUB_CATEGORY_CODE")
                if biz_sub_category_id != "2":  # Check against string '2'
                    biz_sub_category = BizSubCategoryOutput(
                        biz_sub_category_id=biz_sub_category_id,
                        biz_sub_category_name=row.get("SUB_CATEGORY_NAME"),
                        biz_detail_cateogry_count=row.get("DETAIL_CATEGORY_COUNT", 0),
                    )
                    results.append(biz_sub_category)

            return results
    except Exception as e:
        print(f"get_all_classification_sub_category_by_main_category_code Error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        close_connection(connection)


def get_all_classification_detail_category_by_sub_category_code(
    sub_category_code: int,
) -> List[BizDetailCategoryOutput]:
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            results: List[BizDetailCategoryOutput] = []
            select_query = """
            SELECT 
                DETAIL_CATEGORY_CODE,
                DETAIL_CATEGORY_NAME
            FROM 
                CLASSIFICATION
            WHERE 
                SUB_CATEGORY_CODE = %s
            GROUP BY
                DETAIL_CATEGORY_CODE,
                DETAIL_CATEGORY_NAME
            ;
            """

            cursor.execute(select_query, (sub_category_code,))
            rows = cursor.fetchall()

            for row in rows:
                biz_detail_category = BizDetailCategoryOutput(
                    biz_detail_category_id=row.get("DETAIL_CATEGORY_CODE"),
                    biz_detail_category_name=row.get("DETAIL_CATEGORY_NAME"),
                )
                results.append(biz_detail_category)

            return results
    except Exception as e:
        print(f"get_all_classification_detail_category_by_sub_category_code Error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        close_connection(connection)


def select_all_classification_category_by_dynamic_query(
    main_category_code: Optional[str] = None,
    sub_category_code: Optional[str] = None,
    detail_category_code: Optional[str] = None,
) -> List[CategoryListOutput]:

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)
    results: List[CategoryListOutput] = []

    try:
        if connection.open:
            select_query = """
                SELECT
                    CLASSIFICATION_ID,
                    MAIN_CATEGORY_NAME,
                    SUB_CATEGORY_NAME,
                    DETAIL_CATEGORY_NAME
                FROM
                    CLASSIFICATION
                WHERE
                    1=1 
            """

            params = []

            if main_category_code is not None:
                select_query += " AND MAIN_CATEGORY_CODE = %s"
                params.append(main_category_code)
            if sub_category_code is not None:
                select_query += " AND SUB_CATEGORY_CODE = %s"
                params.append(sub_category_code)
            if detail_category_code is not None:
                select_query += " AND DETAIL_CATEGORY_CODE = %s"
                params.append(detail_category_code)

            select_query += " ORDER BY CLASSIFICATION_ID DESC"

            # logger.info(f"Executing query: {select_query}, with params: {params}")
            cursor.execute(select_query, params)

            rows = cursor.fetchall()

            for row in rows:
                category_output = CategoryListOutput(
                    category_id=row.get("CLASSIFICATION_ID"),
                    main_category_name=row.get("MAIN_CATEGORY_NAME"),
                    sub_category_name=row.get("SUB_CATEGORY_NAME"),
                    detail_category_name=row.get("DETAIL_CATEGORY_NAME"),
                )
                results.append(category_output)

        return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
        rollback(connection)
        raise
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        rollback(connection)
        raise
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)
