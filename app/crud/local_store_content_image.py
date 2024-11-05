from app.db.connect import (
    commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from typing import List

load_dotenv()

def insert_store_content_image(store_content_pk: int, image_urls: List):
    # 데이터베이스 연결 설정
    connection = get_re_db_connection()
    cursor = None
    
    try:
        cursor = connection.cursor()
        # 이미지 저장 쿼리
        insert_query = """
            INSERT INTO LOCAL_STORE_CONTENT_IMAGE (LOCAL_STORE_CONTENT_ID, LOCAL_STORE_CONTENT_IMAGE_URL)
            VALUES (%s, %s)
        """
        for image_url in image_urls:
            cursor.execute(insert_query, (store_content_pk, image_url))
        
        commit(connection)
    except Exception as e:
        print("Error:", e)
        rollback(connection)
    finally:
        if cursor:
            close_cursor(cursor)
        close_connection(connection)
