from app.db.connect import get_db_connection

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
        except Exception as e:
            print(f"Error inserting data: {e}")
            connection.rollback()
            raise e
