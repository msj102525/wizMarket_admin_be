import pymysql
from pymysql import OperationalError, InternalError, ProgrammingError, Error

# 연결
def get_db_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="1234",
            database="test",
            autocommit=False,
        )
        print("Database connection established successfully.")
    except OperationalError as e:
        print(f"OperationalError: {e}")
    except InternalError as e:
        print(f"InternalError: {e}")
    except ProgrammingError as e:
        print(f"ProgrammingError: {e}")
    except Error as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return connection


# DB 연결 종료
def close_connection(connection):
    try:
        if connection and connection.open:
            connection.close()
    except pymysql.MySQLError as e:
        print(f"Error closing connection: {e}")



# 커서 종료
def close_cursor(cursor):
    try:
        if cursor and not cursor.closed:
            cursor.close()
    except pymysql.MySQLError as e:
        print(f"Error closing cursor: {e}")


# 커밋
def commit(connection):
    try:
        if connection and connection.open:
            connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error committing transaction: {e}")


# 롤백
def rollback(connection):
    try:
        if connection and connection.open:
            connection.rollback()
    except pymysql.MySQLError as e:
        print(f"Error rolling back transaction: {e}")
