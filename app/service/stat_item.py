from app.crud.stat_item import insert_stat_item


def insert_stat_item_from_loc_info(
    table_name,
    column_name,
):
    # 삽입할 데이터
    table_name = table_name
    column_name = column_name
    reference_id = 5

    # stat_item 테이블에 데이터 삽입
    insert_stat_item(table_name, column_name, reference_id)


# 함수 실행
if __name__ == "__main__":
    insert_stat_item_from_loc_info("population", "mz_population")
