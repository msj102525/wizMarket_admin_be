from app.db.connect import get_db_connection
import mysql.connector  # 예외 처리를 위해 필요

def insert_record(table_name: str, **kwargs):
    with get_db_connection() as connection:
        try:
            with connection.cursor() as cursor:
                columns = ', '.join(kwargs.keys())
                placeholders = ', '.join(['%s'] * len(kwargs))
                values = tuple(kwargs.values())
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, values)
            connection.commit()
        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:  # Duplicate entry error code
                print(f"Duplicate entry found for {kwargs}. Skipping...")
            else:
                print(f"Error inserting data: {e}")
                connection.rollback()
                raise e
        except Exception as e:
            print(f"Error inserting data: {e}")
            connection.rollback()
            raise e
