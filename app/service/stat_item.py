from app.crud.stat_item import insert_stat_item

def insert_stat_item_from_loc_info():
    # 삽입할 데이터
    table_name = "loc_info"
    column_name = "resident"
    source = "sbiz"

    # stat_item 테이블에 데이터 삽입
    insert_stat_item(table_name, column_name, source)



# 함수 실행
if __name__ == "__main__":
    insert_stat_item_from_loc_info()