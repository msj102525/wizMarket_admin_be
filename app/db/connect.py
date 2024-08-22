import pymysql
import os
from dotenv import load_dotenv
from pymysql import OperationalError, InternalError, ProgrammingError, Error

load_dotenv()


def get_db_connection():
    connection = None
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
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
        if connection:
            connection.close()
            print("Database connection closed successfully.")
    except pymysql.MySQLError as e:
        print(f"Error closing connection: {e}")


# 커서 종료
def close_cursor(cursor):
    try:
        if cursor is not None:
            cursor.close()
            print("Cursor closed successfully.")
    except pymysql.MySQLError as e:
        print(f"Error closing cursor: {e}")


# 커밋
def commit(connection):
    try:
        if connection:
            connection.commit()
            print("Transaction committed successfully.")
    except pymysql.MySQLError as e:
        print(f"Error committing transaction: {e}")


# 롤백
def rollback(connection):
    try:
        if connection:
            connection.rollback()
            print("Transaction rolled back successfully.")
    except pymysql.MySQLError as e:
        print(f"Error rolling back transaction: {e}")
