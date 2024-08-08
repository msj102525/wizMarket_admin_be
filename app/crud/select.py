from app.db.connect import get_db_connection

def select_wiz():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM wiz where id = 1")
    row = cursor.fetchone()
    cursor.close()
    connection.close()

    if row:
        result = row[0]  # name 값을 반환
    else:
        result = None

    # 조회 결과를 콘솔에 출력
    print("Query Result:", result)

    return result
