import logging
from typing import List
from fastapi import HTTPException
import pymysql
from dotenv import load_dotenv
from app.db.connect import (
    get_db_connection,
    close_connection,
)
from app.schemas.reference import Reference


def get_all_reference() -> List[Reference]:
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            results: List[Reference] = []
            select_query = "SELECT * FROM REFERENCE;"
            cursor.execute(select_query)
            rows = cursor.fetchall()

            for row in rows:
                reference = Reference(
                    reference_id=row.get("REFERENCE_ID"),
                    reference_name=row.get("REFERENCE_NAME"),
                    reference_url=row.get("REFERENCE_URL"),
                )

                results.append(reference)

            return results
    except Exception as e:
        print(f"get_all_reference Error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        close_connection(connection)
