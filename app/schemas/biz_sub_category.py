class BizSubCategory:
    biz_sub_category_id: int
    biz_main_category_id: int
    biz_sub_categoty_name: str

    class Config:
        from_attributes = True
