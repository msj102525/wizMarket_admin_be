from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback

# stat_item 테이블에 데이터 삽입
def insert_stat_item(table_name, column_name, source):
    connection = None
    cursor = None
    try:
        # DB 연결
        connection = get_db_connection()
        cursor = connection.cursor()

        # stat_item 테이블에 데이터 삽입하는 SQL 쿼리 작성
        insert_query = """
            INSERT INTO stat_item (table_name, column_name, source)
            VALUES (%s, %s, %s)
        """
        
        # 데이터 삽입
        cursor.execute(insert_query, (table_name, column_name, source))

        # 커밋
        commit(connection)

        print(f"Data inserted successfully into stat_item with table_name={table_name}, column_name={column_name}, source={source}")
    
    except Exception as e:
        print(f"Error inserting into stat_item: {e}")
        # 문제가 생기면 롤백
        rollback(connection)
    
    finally:
        # 커서와 연결 종료
        close_cursor(cursor)
        close_connection(connection)
